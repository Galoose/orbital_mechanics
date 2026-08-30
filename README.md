# orbital_mechanics
 
A small orbital mechanics library. Create a satellite object, two orbits, and use built-in functions to solve for orbital transfers. Change in satellite mass and Δv for the transfer and each impulse is found.
 
## Example code
 
```python
Re: int     = 6378  # Earth radius in km
start_orbit = (Re + 250) * 10**3
final_orbit = 42164.154 * 10**3
 
print("Starting Hohmann transfer:")
 
my_satellite = Satellite(m_i=5_192, isp=450.5)
 
orbit_i: Orbit = Orbit(
    orbit_type="circ",
    satellite=my_satellite,
    r=start_orbit)
 
orbit_f: Orbit = Orbit(
    orbit_type="circ",
    satellite=my_satellite,
    r=final_orbit)
 
hohmann_transfer = hohmann(
    satellite=my_satellite,
    orbit_i=orbit_i,
    orbit_f=orbit_f)
 
print("-- Extracted data --")
print(f"Transfer time: {hohmann_transfer.time_elapsed}")
print(f"\tInitial orbit velocity: {hohmann_transfer.maneuvers[0].v_i / 1000:.4g}km/s, "
      f"Transfer perigee velocity: {hohmann_transfer.maneuvers[0].v_f / 1000:.4g}km/s, "
      f"Transfer apogee velocity: {hohmann_transfer.maneuvers[1].v_i / 1000:.4g}km/s, "
      f"Final orbit velocity: {hohmann_transfer.maneuvers[1].v_f / 1000:.4g}km/s")
 
print("----")
print(f"{hohmann_transfer.transfer_type} transfer from r {start_orbit:.4g}km "
      f"to r {final_orbit:.4g}km: Δv = {hohmann_transfer.total_v / 1000:.4g}km/s, "
      f"Δm = {hohmann_transfer.total_m:.4g}kg")
print("----\n\n")
```
 
## Example output
 
```text
Starting Hohmann transfer:
180.0 180.0
  Impulse solution (1) - Δv: 2.441km/s, γ: 0deg
180.0 180.0
  Impulse solution (2) - Δv: 2.441km/s, γ: 0deg
Transfer no. 1: Δv = 2.441km/s, Δm = 2204kg
180.0 180.0
  Impulse solution (1) - Δv: 1.473km/s, γ: -0deg
180.0 180.0
  Impulse solution (2) - Δv: 1.473km/s, γ: -0deg
Transfer no. 2: Δv = 1.473km/s, Δm = 847kg
-- Extracted data --
Transfer time: 5:15:54.675635
  Initial orbit velocity: 7.758km/s,
  Transfer perigee velocity: 10.2km/s,
  Transfer apogee velocity: 1.603km/s,
  Final orbit velocity: 3.076km/s
----
Hohmann transfer from r 6.628e+06km to r 4.216e+07km:
  Δv = 3.913km/s,
  Δm = 3051kg
----
Starting Bi-Elliptic transfer:
180.0 180.0
  Impulse solution (1) - Δv: 3.062km/s, γ: 0deg
180.0 180.0
  Impulse solution (2) - Δv: 3.062km/s, γ: 0deg
Transfer no. 1: Δv = 3.062km/s, Δm = 646.8kg
180.0 180.0
  Impulse solution (1) - Δv: 0.609km/s, γ: -0deg
180.0 180.0
  Impulse solution (2) - Δv: 0.609km/s, γ: -0deg
Transfer no. 2: Δv = 0.609km/s, Δm = 66.04kg
8.537736462515939e-07 8.537736462515939e-07
  Impulse solution (1) - Δv: 0.4478km/s, γ: -180deg
359.99999914622634 359.99999914622634
  Impulse solution (2) - Δv: 0.4478km/s, γ: 180deg
Transfer no. 3: Δv = 0.4478km/s, Δm = 40.54kg
-- Extracted data --
Transfer time: 7 days, 8:39:00.634789
  Initial orbit velocity: 7.716km/s,
  Transfer perigee velocity: 10.78km/s,
  Transfer 1 apogee velocity: 0.2694km/s,
  Transfer 2 apogee velocity: 0.8785km/s,
  Transfer 2 perigee velocity: 2.51km/s,
  Final orbit velocity: 2.062km/s
----
Bi-elliptic transfer from r 6.7e+06km to r 9.38e+07km:
Δv = 4.119km/s,
Δm = 753.4kg
----
Starting single impulse transfer between two intersecting orbits:
139.78682068619455 114.78682068619455
  Impulse solution (1) - Δv: 0.8001km/s, γ: 86.23deg
337.8371223793449 312.8371223793449
  Impulse solution (2) - Δv: 0.7983km/s, γ: -84.55deg
Transfer no. 1: Δv = 0.7983km/s, Δm = 418.8kg
```
 
