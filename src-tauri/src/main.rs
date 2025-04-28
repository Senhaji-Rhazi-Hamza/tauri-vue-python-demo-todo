//! src-tauri/src/main.rs
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::{
    env,
    io::{BufRead, BufReader},
    net::TcpStream,
    path::PathBuf,
    process::{Child, Command, Stdio},
    sync::{Arc, Mutex},
    thread,
    time::{Duration, Instant},
};
use tauri::{App, AppHandle, Builder, Emitter, RunEvent, WindowEvent};

#[cfg(unix)]
use libc;
#[cfg(unix)]
use std::os::unix::process::CommandExt; // for pre_exec // now resolved

/// Returns `"python_backend.exe"` on Windows or `"python_backend"` elsewhere.
fn backend_filename() -> &'static str {
    if cfg!(windows) {
        "python_backend.exe"
    } else {
        "python_backend"
    }
}

/// Spawn the frozen Python side-car from the same folder as this exe,
/// piping its stdout/stderr into the console.
fn spawn_backend() -> std::io::Result<Child> {
    let exe_dir: PathBuf = env::current_exe()?
        .parent()
        .expect("exe has no parent")
        .to_path_buf();
    let bin = exe_dir.join(backend_filename());
    println!("▶ spawning backend: {:?}", bin);

    let mut cmd = Command::new(&bin);
    cmd.stdout(Stdio::piped()).stderr(Stdio::piped());

    // On Unix, detach into its own process group so we can kill everything
    #[cfg(unix)]
    unsafe {
        cmd.pre_exec(|| {
            if libc::setsid() < 0 {
                return Err(std::io::Error::last_os_error());
            }
            Ok(())
        });
    }

    let mut child = cmd.spawn()?;

    // pipe stdout → println!
    if let Some(out) = child.stdout.take() {
        thread::spawn(move || {
            for line in BufReader::new(out).lines().flatten() {
                println!("[backend] {line}");
            }
        });
    }

    // pipe stderr → eprintln!
    if let Some(err) = child.stderr.take() {
        thread::spawn(move || {
            for line in BufReader::new(err).lines().flatten() {
                eprintln!("[backend-err] {line}");
            }
        });
    }

    Ok(child)
}

/// Poll port 8000 until it's open, then emit `"backend-ready"` globally.
fn monitor_backend_ready(app_handle: &AppHandle) {
    let handle = app_handle.clone();
    thread::spawn(move || {
        let deadline = Instant::now() + Duration::from_secs(10);
        while Instant::now() < deadline {
            if TcpStream::connect(("127.0.0.1", 8000)).is_ok() {
                println!("✅ backend is ready");
                let _ = handle.emit("backend-ready", ());
                return;
            }
            thread::sleep(Duration::from_millis(100));
        }
        eprintln!("⚠️ backend did not become ready in 10s");
    });
}

/// Kill & wait on the backend any time the window closes or the app exits.
fn kill_on_exit(handle: Arc<Mutex<Option<Child>>>, event: &RunEvent) {
    let should_kill = matches!(
        event,
        // User clicked the “X”
        RunEvent::WindowEvent { event: WindowEvent::CloseRequested { .. }, .. }
      // Tauri is about to exit (before Exit)
      | RunEvent::ExitRequested { .. }
      // Final exit event
      | RunEvent::Exit
    );
    if should_kill {
        if let Some(mut child) = handle.lock().unwrap().take() {
            #[cfg(unix)]
            {
                let pgid = child.id() as i32;
                unsafe { libc::kill(-pgid, libc::SIGKILL) };
            }
            #[cfg(windows)]
            {
                let _ = child.kill();
            }
            let _ = child.wait();
            println!("⛔ backend terminated, port 8000 freed");
        }
    }
}

fn main() {
    // Shared handle for the Python child process
    let child_handle = Arc::new(Mutex::new(None));

    Builder::default()
        .setup({
            let child_handle = child_handle.clone();
            move |app: &mut App| {
                // Skip auto-spawn if TAURI_DEV=1 (run Sanic manually in dev)
                if env::var("TAURI_DEV").unwrap_or_default() != "1" {
                    let child = spawn_backend().expect("failed to spawn python backend");
                    *child_handle.lock().unwrap() = Some(child);
                    // Monitor readiness in background
                    monitor_backend_ready(app.handle());
                } else {
                    println!("⚠️ TAURI_DEV=1 → skipping backend spawn");
                }
                Ok(())
            }
        })
        .invoke_handler(tauri::generate_handler![demo_todo_ru_py_lib::py_api])
        .build(tauri::generate_context!())
        .expect("error building Tauri")
        .run(move |_app, event| {
            kill_on_exit(child_handle.clone(), &event);
        });
}
