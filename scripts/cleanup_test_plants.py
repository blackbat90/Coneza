import sqlite3

conn = sqlite3.connect('/data/coneza_backend.db')
cursor = conn.cursor()

# Remove temporary test plant
cursor.execute("DELETE FROM plants WHERE id != 'plant-solar-west-01'")
cursor.execute("UPDATE devices SET plant_id = 'plant-solar-west-01' WHERE device_id = 'coneza-edge-solar-park-01'")
cursor.execute("UPDATE documents SET plant_id = 'plant-solar-west-01' WHERE device_id = 'coneza-edge-solar-park-01'")
conn.commit()

cursor.execute("SELECT id, name, site_type, installed_capacity_kw FROM plants")
print("Cleaned plants in DB:")
for row in cursor.fetchall():
    print(row)

conn.close()
