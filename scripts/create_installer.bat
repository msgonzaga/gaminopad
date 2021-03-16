:: Remember to activate the virtual environment before running this script
pyinstaller --onedir --noconsole --noconfirm --icon ../ico/gaminoicon.ico --clean^
 --specpath ../spec --distpath ../dist --workpath ../build -n gaminopad ../main.py
xcopy ..\ico\gaminoicon.ico ..\dist\gaminopad\ico\
xcopy ..\config\config.yml ..\dist\gaminopad\config\
rd /s /q ..\spec
rd /s /q ..\build