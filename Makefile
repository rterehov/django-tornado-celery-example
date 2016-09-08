default: _requirements db end

_requirements:
	@echo "Install common requirements"
	@pip install --exists-action=s -r requirements/common.txt

req: _requirements

db: migrate


migrate:
	@echo "Running migrations"
	@python manage.py migrate -v 1 --traceback

collectstatic:
	@echo "Collect static"
	@python manage.py collectstatic --noinput -v 1

end:
	@echo "Make complete ok"
