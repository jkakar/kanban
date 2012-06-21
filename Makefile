build:
	pip install -r requirements.txt

clean:
	find . -name \*pyc -exec rm {} \;

check:
	@trial kanban

info:
	@git status
	@echo
	@echo "Lines of application code:"
	@find kanban -name \*py | grep -v test_ | xargs cat | wc -l
	@echo
	@echo "Lines of test code:"
	@find kanban -name \*py | grep test_ | xargs cat | wc -l
