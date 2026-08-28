@echo off
REM このリポジトリのノートブックをローカルのJupyterで開くための起動スクリプト。
REM ダブルクリックするか、コマンドプロンプトで実行してください。
cd /d "%~dp0notebooks"
echo Jupyter Notebookを起動します。ブラウザが自動で開きます...
python -m notebook
