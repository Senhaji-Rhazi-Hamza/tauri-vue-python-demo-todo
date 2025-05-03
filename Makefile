BACKEND_NAME:=python_backend

HOST_ARCH := $(shell rustc -vV | grep host | awk '{print $$2}')


build-python-bin:
	uv  --directory src-backend run pyinstaller run.py \
	--onefile \
	--name ${BACKEND_NAME} \
	--clean \
	--log-level=DEBUG \
	--collect-all sqlalchemy \
	--collect-all platformdirs \
	--collect-all tracerite  


copy-python-bin: build-python-bin
	mkdir src-tauri/binaries || echo  "folder binaries exist"
	cp src-backend/dist/${BACKEND_NAME} src-tauri/binaries/$(BACKEND_NAME)-$(HOST_ARCH)

build-app: copy-python-bin
	cd src-tauri && npm run tauri build


run-dev-ui:
	cd src-tauri && export TAURI_DEV=1 && npm run tauri dev

run-dev-backend:
	uv --directory src-backend run python main.py 


