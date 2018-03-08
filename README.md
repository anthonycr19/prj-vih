# Proyecto VIH


## Despliegue

```sh
$ pip install -r requirements/dev.txt
$ python manage.py migrate
$ python manage.py collectstatic
$ find ./apps -name '*.json' -exec python manage.py loaddata {} \;
```

## Variables de Entorno

* `SECRET_KEY` Secret Key de Django.
* `ALLOWED_HOSTS` Lista de dominios permitidos para acceder a la aplicación.
* `DB_NAME` nombre de la base de datos.
* `DB_USER` usuario de la base de datos.
* `DB_PASSWORD` contraseña del usuario de la base de datos.
* `DB_HOST` servidor de base de datos.
* `DB_PORT` puerto de la base de datos.
* `APP_IDENTIFIER` Identificador de la aplicación.
* `INMUNIZACIONES_HOST_URL` Ruta de inmunizaciones
* `LOGIN_DOMAIN` Dominio del login.
* `LOGIN_HOST_URL` Ruta del login.
* `CITAS_API_HOST` Ruta del api de citas.
* `CITAS_API_TOKEN` Token del api de citas.
* `MPI_API_HOST` Ruta del api de mpi..
* `MPI_CLIENT_ID` Token del api de mpi.
* `CATALOGO_ODOO_TOKEN` Token para catalogo de ODOO.
* `CATALOGO_ODOO_HOST_URL` URL para la consulta del servicio de examenes
* `UPS_LABORATORIO` UPS default para el servicio de laboratorio
* `UPS_EGRESO` UPS default para el servicio de egreso

## Carga de data inicial:

```bash
python manage.py loaddata apps/afiliacion/fixtures/lugarabordaje.json
python manage.py loaddata apps/afiliacion/fixtures/poblaciones.json
python manage.py loaddata apps/afiliacion/fixtures/establecimientos.json
```
