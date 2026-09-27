echo "Building Bus Finder project..."
python3 -m pip install -r requirements.txt
python3 manage.py collectstatic --noinput --clear
python3 manage.py migrate
python3 manage.py seed_buses
echo "Build complete!"
