@echo off
pyuic5 ./designer/field_options.ui -o ./src/forms/field_options.py &&^
pyuic5 ./designer/list.ui -o ./src/forms/list.py &&^
pyuic5 ./designer/keyboard.ui -o ./src/forms/keyboard.py &&^
pyuic5 ./designer/options.ui -o ./src/forms/options.py &&^
pyuic5 ./designer/practice.ui -o ./src/forms/practice.py &&^
pyuic5 ./designer/questions_wizard.ui -o ./src/forms/questions_wizard.py &&^
pyuic5 ./designer/summary.ui -o ./src/forms/summary.py &&^
pyuic5 ./designer/template_wizard.ui -o ./src/forms/template_wizard.py^