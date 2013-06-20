all:
	pyuic4 downloadwidget.ui -o downloadwidget.py
	pyuic4 main.ui -o main.py
	pyuic4 selectwidget.ui -o selectwidget.py
	pyuic4 streamwidget.ui -o streamwidget.py
