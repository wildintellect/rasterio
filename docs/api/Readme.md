# Generate the api docs

```sh
#Starting from the project root
cd docs/
sphinx-apidoc -f -P -F -H rasterio -A "Sean Gillies" -V 0.30 -R 0.30 -o api ../rasterio/
cd api
make html
```
