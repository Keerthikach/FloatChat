import xarray as xr

# Load your NetCDF file
file_path = "1900121_prof.nc"
ds = xr.open_dataset(file_path)

print("Variables in dataset:", list(ds.variables))

# Extract arrays
lat = ds['LATITUDE'].values  # array
lon = ds['LONGITUDE'].values  # array
temp = ds['TEMP'].values  # 2D array: depth x profile
pres = ds['PRES'].values  # depth (pressure)

print("Latitude shape:", lat.shape)
print("Longitude shape:", lon.shape)
print("Temperature shape:", temp.shape)
print("Pressure shape:", pres.shape)

# Example: first profile
print("\nFirst profile:")
print("Lat:", lat[0])
print("Lon:", lon[0])
print("Pressure:", pres[0, :10])      # first 10 depth levels
print("Temperature:", temp[0, :10])  # corresponding temperatures
