import datetime
import numpy as np

def generate_chi2_script(
        histo_name : str, 
        critical_value : float,
        muhat : float, 
        lower : float, upper : float, 
        mu_values : np.ndarray,
        chi2_vals : np.ndarray) -> str:
    """
    Generates a matplotlib plot of chi2 vs mu
    """

    mu_values = np.array2string(np.array(mu_values), separator=', ')
    chi2_vals = np.array2string(np.array(chi2_vals), separator=', ')

    return f'''
#!/usr/bin/env python3
# Auto-generated chi2 plot script for {histo_name}
# Generated on {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

import numpy as np
import matplotlib.pyplot as plt

import os

# Output location
plotDir = os.path.split(os.path.realpath(__file__))[0]
if 'YODA_USER_PLOT_PATH' in globals():
    plot_outdir = globals()['YODA_USER_PLOT_PATH']
else:
    plot_outdir = plotDir

# Plot parameters
histo_name = "{histo_name}"
mu_hat = float({muhat})
try:
    lower_limit = float({lower})
except:
    lower_limit = None
try:
    upper_limit = float({upper})
except:
    upper_limit = None

critical_value = float({critical_value})

# Pre-calculated data points
mu_values = np.array({mu_values})
chi2_vals = np.array({chi2_vals})


# Create plot
fig, ax = plt.subplots()
ax.plot(mu_values, chi2_vals, label=r'$\\chi^2(\\mu)$', color='black')
ax.set_xlabel(r'$\\mu$')

# Critical value of test
ax.axhline(critical_value, color='red', linestyle='--', 
        label=r'$\\chi^2$ = {{:.3g}}'.format(critical_value))

# Plot mu limits
if lower_limit is not None:
    ax.axvline(lower_limit, color='green', linestyle=':', 
            label=r'$\\mu_{{{{down}}}}$ = {{:.3g}}'.format(lower_limit))
if upper_limit is not None:
    ax.axvline(upper_limit, color='blue', linestyle=':', 
            label=r'$\\mu_{{{{up}}}}$ = {{:.3g}}'.format(upper_limit))

# Plot mu_hat
if mu_hat is not None:
    ax.axvline(mu_hat, color='purple', linestyle='-.', 
            label=r'$\\hat\\mu$ = {{:.3g}}'.format(mu_hat))

ax.legend()

# Format ticks
ax.tick_params(axis='both', which='both', direction='in', top=True, right=True)
ax.minorticks_on()
ax.tick_params(axis='both', which='minor', direction='in', top=True, right=True)

output_path = os.path.join(plot_outdir, histo_name+'_chi2')
# Save the plot
fig.savefig(output_path + '.pdf', format='PDF')
fig.savefig(output_path + '.png', format='PNG')
plt.close(fig)

'''
