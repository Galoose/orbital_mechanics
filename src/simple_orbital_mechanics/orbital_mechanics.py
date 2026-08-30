import math
import sys
import datetime

# To-Do: TLE integration, orbit pathfinding

def mu(m1: float, m2: float) -> float:
    """Calclates mu (km^3/s^2) given two objects, one orbiting the other.

    Args:
        m1 : mass of central object (kg)
        m2 : mass of orbiting object (kg)

    Returns:
        mu.
    """
    G: float = 6.67 * 10**(-11) # gravitational constant
    return G * (m1 + m2)

class Satellite:
    """Contains information reguarding the orbital satellite.

    Args:
        m_i : initial mass (kg)
        isp : specific impulse (s)
        m_c : current mass (kg)
        m1  : mass of the central body, typically Earth (kg)
        mu  : constant defined by mu function, updates when satellite mass changes
    """
    def __init__(self, m_i: float, isp: float, m1: float = 5.98 * 10**24):
        self.m_i = m_i
        self.isp = isp
        self.m_c = m_i
        self.m1  = m1
        self.mu  = mu(self.m1, self.m_c)

    def update_fuel(self, delta_m: float):
        self.m_c -= delta_m
        self.mu  = mu(self.m1, self.m_c)

class OrbitError(Exception):
    pass

class Orbit:
    """Defines and stores orbit parameters.

    Attriutes:
        orbit_type : circular (circ), elliptical (ellip)
        satellite  : object containing information about satellite in orbit
        r          : circular orbit radius (m)
        r_p        : elliptical periapsis radius (m)
        r_a        : elliptical apoapsis radius (m)
        rot        : rotation angle of the apse line (deg)
    """
    def __init__(self, orbit_type: str, satellite: Satellite, r: float = None, r_p: float = None, r_a: float = None, rot: float = 0):
        self.orbit_type = orbit_type
        self.satellite  = satellite
        self.r          = r
        self.r_p        = r_p
        self.r_a        = r_a
        self.rot        = rot
        match self.orbit_type:
            case "circ":
                if self.r is None: raise OrbitError(f"Insufficient information given for orbit of type {orbit_type}!")
                self.a = self.r_p = self.r_a = self.r
                self.e = 0
                self.p = self.a
            case "ellip":
                if (self.r_p or self.r_a) is None: raise OrbitError(f"Insufficient information given for orbit of type {orbit_type}!")
                self.a = 0.5 * (self.r_a + self.r_p)
                self.e = (self.r_a - self.r_p)/(self.r_a + self.r_p)
                self.p = self.a * (1 - self.e**2)
        self.h = math.sqrt(2 * self.satellite.mu) * math.sqrt((self.r_a * self.r_p)/(self.r_a + self.r_p))
        self.T = ((2 * math.pi) / math.sqrt(self.satellite.mu)) * self.a**(3/2)


class MassError(Exception):
    pass

class Transfer:
    """Stores information on orbital transfers for later extraction.

    Attributes:
        transfer_type : a record of the transfer performed
        satellite     : object containing information about satellite in orbit
        total_v       : total 󰇂v required for the transfer (m/s)
        total_m       : total mass of fuel used in transfer (kg)
        total_t       : culmative transfer time (s)
        maneuvers     : a list containing Maneuver instances
    Exceptions:
        Mass error : delta_m exceeds initial mass.
    """
    class Maneuver:  # Can I add orbit type (from Orbit obj. below) and use to automate final velo breakdown msg?
        """A helper used to store information reguarding each impulse maneuver.

        Args:
            number  : what order was this maneuver in the transfer?
            v_i     : initial orbital velocity (m/s)
            v_f     : final orbital velocity (m/s)
            delta_v : change in orbital velocity (m/s)
            delta_m : change in mass (fuel burned) (kg)
        """
        def __init__(self, number: int, v_i: float, v_f: float, delta_v: float, delta_m: float, gamma: float):
            self.number = number
            self.v_i = v_i
            self.v_f = v_f
            self.delta_v = delta_v
            self.delta_m = delta_m
            self.gamma   = gamma

    def __init__(self, transfer_type: str, satellite: Satellite):
        self.transfer_type = transfer_type
        self.satellite = satellite
        self.total_v   = 0
        self.total_m   = 0
        self.total_t   = 0
        self.maneuvers = []

    def mass_check(self):
        """Throws error if attempting to use more fuel than stored onboard vessel."""
        if self.total_m > self.satellite.m_i:
            raise MassError("Error: Fuel mass exceeds initial mass!")

    def transfer_impulse(self, v_i: float, v_f: float, delta_v: float, delta_m: float, gamma: float):
        """Individual step of the transfer.

        Args:
            v_i     : initial orbital velocity (m/s)
            v_f     : final orbital velocity (m/s)
            delta_v : change in orbital velocity (m/s)
            delta_m : change in mass (fuel burned) (kg)
        """
        self.total_v += abs(delta_v)
        self.total_m += delta_m
        self.satellite.update_fuel(delta_m)
        new_maneuver: self.Maneuver = self.Maneuver(len(self.maneuvers) + 1, v_i, v_f, delta_v, delta_m, gamma)
        self.maneuvers.append(new_maneuver)
        print(f"Transfer no. {new_maneuver.number}: 󰇂v = {delta_v / 1000:.4g}km/s, 󰇂m = {delta_m:.4g}kg")
        try:
            self.mass_check()
        except MassError as e:
            print(f"{e}")

    
    def transfer_time(self, T: float):
        """Sets & stores elapsed transfer time.

        Args:
            T : time in seconds to complete the transfer
        """
        self.total_t += T
        self.time_elapsed = str(datetime.timedelta(seconds=self.total_t))


def drag(p, A, v, cd) -> float:
    """Calculate the drag experienced on a satellite in LEO.

    Args:
        p  : atmosphere density (kg/m^3)
        A  : cross section facing motion (m^2)
        v  : velocity (km/s)
        cd : drag coefficient

    Returns:
        The drag force effective on the satellite.
    """
    return 0.5 * p * v**2 * A * cd



def fuel_burn(satellite: Satellite, delta_m: float = None, delta_v: float = None, g: float = 9.807) -> float:
    """Calculates change of velocity OR mass for a satellite maneuver, given change in velocity OR mass.

    Args:
        satellite  : object containing information about satellite in orbit
        delta_m    : (optional) change of mass eg fuel burnt (kg)
        delta_v    : (optional) change of velocity (m/s)
        g          : earth gravity (m/s^2)

    Returns:
        The change in velocity (m/s) OR mass (kg) for a satellite maneuver.
    """
    unkn_val: str | None = next((key for key, value in locals().items() if value == None), None)
    match unkn_val:
        case "delta_m":
            result = satellite.m_c * (1 - math.e**(-delta_v/(satellite.isp * g)))
        case "delta_v":
            result = -math.log(1 - (delta_m / satellite.m_c)) * (satellite.isp * g)
        case None:
            sys.exit("Must include a value for either delta_m or delta_v!")
    return result


def impulse(orbit_i: Orbit, orbit_t: Orbit) -> list[float]:
    """Calculates a single orbital impulse maneuver between orbits.

    Args:
        o_i       : inital orbit (obj)
        o_t       : target orbit (obj)

    Returns:
        Initial velocity (m/s), final velocity (m/s), change in velocity (m/s), mass lost (kg).
    """
    if orbit_i.satellite is not orbit_t.satellite:
        sys.exit("Orbit satellites are not the same!")
    else:
        satellite = orbit_i.satellite

    eta   = math.radians(orbit_t.rot - orbit_i.rot)
    a     = orbit_i.e * orbit_t.p - orbit_t.e * orbit_i.p * math.cos(eta)
    b     = -orbit_t.e * orbit_i.p * math.sin(eta)
    c     = orbit_i.p - orbit_t.p
    try:
        alpha = math.atan(b/a)
    except:
        alpha = math.copysign(1, b) * math.pi / 2

    try:
        nu_i  = (alpha + math.acos(c/a * math.cos(alpha))) % (2*math.pi), (alpha - math.acos(c/a * math.cos(alpha))) % (2*math.pi)
    except:
        nu_i = (alpha + math.pi) % (2*math.pi), (alpha - math.pi) % (2*math.pi)
    nu_f  = (nu_i[0] - eta) % (2*math.pi), (nu_i[1] - eta) % (2*math.pi)


    solutions = {}
    for i in range(2):
        print(math.degrees(nu_i[i]), math.degrees(nu_f[i]))
        r     = orbit_i.p / (1 + orbit_i.e * math.cos(nu_i[i]))

        vp_i  = orbit_i.h / r
        vp_f  = orbit_t.h / r

        vr_i  = satellite.mu / orbit_i.h * orbit_i.e * math.sin(nu_i[i])
        vr_f  = satellite.mu / orbit_t.h * orbit_t.e * math.sin(nu_f[i])

        v_i   = math.sqrt(vp_i**2 + vr_i**2)
        v_f   = math.sqrt(vp_f**2 + vr_f**2)

        phi_i = math.atan2(vr_i, vp_i)
        phi_f = math.atan2(vr_f, vp_f)

        delta_v = math.sqrt(v_i**2 + v_f**2 - 2 * v_i * v_f * math.cos(phi_f - phi_i))
        gamma   = math.atan2(vr_f - vr_i, vp_f - vp_i)

        solutions[i] = {"r": r, "v_i": v_i, "v_f": v_f, "delta_v": delta_v, "gamma": gamma}

        print(f"\tImpulse solution ({i+1}) - 󰇂v: {delta_v / 1000:.4g}km/s, 󱃮: {round(math.degrees(gamma), 4):.4g}deg")
        
    if abs(solutions[0]["delta_v"]) < abs(solutions[1]["delta_v"]):
        r = solutions[0]["r"]
        v_i = solutions[0]["v_i"]
        v_f = solutions[0]["v_f"]
        delta_v = solutions[0]["delta_v"]
        gamma = solutions[0]["gamma"]

    delta_m = abs(fuel_burn(satellite = satellite, delta_v = delta_v))  

    return v_i, v_f, delta_v, delta_m, gamma


def hohmann(satellite: Satellite, orbit_i: Orbit, orbit_f: Orbit) -> Transfer:
    """Calculates change in velocity and mass for a Hohmann transfer, given initial and final orbit conditions.

    Args:    
        satellite : object containing information about satellite in orbit    
        orbit_i   : starting orbit conditions
        orbit_f   : final orbit conditions

    Returns:
        Transfer object containing all relevant data.
    """
    hohmann_transfer = Transfer("Hohmann", satellite)

    orbit_t: Orbit = Orbit(orbit_type = "ellip", satellite = satellite, r_p = orbit_i.r, r_a = orbit_f.r)
    
    hohmann_transfer.transfer_impulse(*impulse(orbit_i, orbit_t))
    hohmann_transfer.transfer_time(orbit_t.T / 2)
    hohmann_transfer.transfer_impulse(*impulse(orbit_t, orbit_f))

    return hohmann_transfer


def bielliptic(satellite: Satellite, orbit_i: Orbit, orbit_f: Orbit) -> Transfer:
    """Calculates change in velocity and mass for a bi-elliptic transfer, given initial and final orbit conditions.

    Args:      
        satellite : object containing information about satellite in orbit  
        orbit_i   : starting orbit conditions
        orbit_f   : final orbit conditions

    Returns:
        Transfer object containing all relevant data.
    """
    bielliptic_transfer = Transfer("Bi-elliptic", satellite = satellite)
    r_m = 40 * orbit_i.r

    orbit_t1 : Orbit = Orbit(orbit_type = "ellip", satellite = satellite, r_p = orbit_i.r, r_a = r_m)
    orbit_t2 : Orbit = Orbit(orbit_type = "ellip", satellite = satellite, r_p = orbit_f.r, r_a = r_m)

    bielliptic_transfer.transfer_impulse(*impulse(orbit_i,  orbit_t1))
    bielliptic_transfer.transfer_time(orbit_t1.T / 2)
    bielliptic_transfer.transfer_impulse(*impulse(orbit_t1, orbit_t2))
    bielliptic_transfer.transfer_time(orbit_t2.T / 2)
    bielliptic_transfer.transfer_impulse(*impulse(orbit_t2, orbit_f))

    return bielliptic_transfer


# Implement plane change maneuver - integrated with above classes!!
# https://www.astronomicalreturns.com/p/section-46-interesting-orbital.html
def nonHohmann(satellite: Satellite, orbit_i: Orbit, orbit_f: Orbit) -> Transfer:
    """Generalisation of non-hohmann transfers with different apse lines.

    Args:      
        satellite : object containing information about satellite in orbit  
        orbit_i   : starting orbit conditions
        orbit_f   : final orbit conditions

    Returns:
        Transfer object containing all relevant data.
    """
    nonHohmann = Transfer("nhohm", satellite = satellite)

    nonHohmann.transfer_impulse(*impulse(orbit_i, orbit_f))

    return nonHohmann