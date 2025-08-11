# entity-type-local-python-package

Should be similar to data-source-package-python-package<br>
To create local package and remote package layers (not to create GraphQL and REST-API layers)

#database scripts
Please place <table-name>.py in /db
No need for seperate file for _ml table

<table-name]_insert.py to create records

Update the setup.py (i.e.name)

#Versions
[pub] 0.0.28 We added get_test_entity_type_id() to support tests in database-mysql-local-python-package
[pub] 0.0.29 We changes EntitiesType to EntityTypesLocal


TODO Do we need seperate repo for entity-type, system, ... or we should use sql2code in circlez-local-python