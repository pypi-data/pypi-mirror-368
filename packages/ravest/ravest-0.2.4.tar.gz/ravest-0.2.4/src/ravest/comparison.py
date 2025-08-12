import logging
logging.basicConfig(level=logging.INFO)
import harmonic as hm
import numpy as np
import getdist.plots

def compute_evidence(fitter, discard=0, thin=1, training_proportion=0.5, epochs_num=20, model_type="RealNVP",  model_kwargs=None):
    """Compute evidence for a fitted model using harmonic.
    
    Parameters
    ----------
    fitter : ravest.fit.Fitter
        Fitted Fitter object with completed MCMC sampling
    discard : int, optional
        Number of burn-in steps to discard (default: 0)
    thin : int, optional
        Thinning factor for chains (default: 1)
    training_proportion : float, optional
        Proportion of chains to use for training (default: 0.5)
    epochs_num : int, optional
        Number of epochs for training the model (default: 20)
    model_type : str, optional
        Harmonic flow model type (default: "RealNVP")
    model_kwargs : dict, optional
        Additional keyword arguments to pass to the harmonic model constructor
        
    Returns
    -------
    ln_evidence : float
        Log evidence estimate
    ln_evidence_std : tuple
        Standard error on log evidence estimate as (lower_bound, upper_bound)
    """
    if not hasattr(fitter, 'sampler'):
        raise ValueError("Fitter must have completed MCMC sampling (sampler attribute missing)")
    
    # Get samples and log probabilities from emcee sampler
    samples = fitter.get_samples_np(discard=discard, thin=thin, flat=False)  # shape: (nsteps, nwalkers, ndim)
    lnprob = fitter.get_sampler_lnprob(discard=discard, thin=thin, flat=False)  # shape: (nsteps, nwalkers)
    logging.info(f"Samples shape: {samples.shape}, Log probabilities shape: {lnprob.shape}")


    # Harmonic expects 
    # (nwalkers, nsteps, ndim) for samples
    # and (nsteps, nwalkers) for log probabilities
    samples_transposed = np.ascontiguousarray(samples.transpose(1, 0, 2))
    lnprob_transposed = np.ascontiguousarray(lnprob.T)
    logging.info(f"Transposed samples shape: {samples_transposed.shape}, Transposed log probabilities shape: {lnprob_transposed.shape}")
    
    # Instantiate harmonic's chains class
    chains = hm.Chains(fitter.ndim)
    chains.add_chains_3d(samples_transposed, lnprob_transposed)
    
    # Split chains for training and inference
    chains_train, chains_infer = hm.utils.split_data(chains, training_proportion=training_proportion)
    
    # Handle model kwargs
    if model_kwargs is None:
        model_kwargs = {}
    
    # TODO: add support for all model types available in harmonic
    # Select and train the machine learning model
    if model_type == "RealNVP":
        default_kwargs = {
            "n_scaled_layers": 2,
            "n_unscaled_layers": 4,
            "standardize": True,  # TODO: investigate setting default to False
            "temperature": 0.8
            }
        default_kwargs.update(model_kwargs)  # User-provided kwargs override defaults
        model = hm.model.RealNVPModel(fitter.ndim, **default_kwargs)
    else:
        raise ValueError(f"Unsupported model type: {model_type}. Available: 'RealNVP'")

    model.fit(chains_train.samples, epochs=epochs_num, verbose=True)

    # TODO: this might be better as a separate function
    # Posterior triangle plot
    samples = samples.reshape(-1, fitter.ndim)  # Flatten samples for plotting
    samp_num = samples.shape[0]
    flow_samples = model.sample(samp_num)
    hm.utils.plot_getdist_compare(samples, flow_samples)


    # Compute evidence
    ev = hm.Evidence(chains_infer.nchains, model)
    ev.add_chains(chains_infer)
    
    # Use log-space evidence to avoid overflow
    ln_inv_evidence = ev.ln_evidence_inv
    err_ln_inv_evidence = ev.compute_ln_inv_evidence_errors()
    
    # Convert to log evidence (negative of log inverse evidence)
    ln_evidence = -ln_inv_evidence
    ln_evidence_std = err_ln_inv_evidence  # This is already in log space
    
    return ln_evidence, ln_evidence_std


def compare_models(fitters, names=None, **kwargs):
    """Compare multiple fitted models using evidence estimates.
    
    Parameters
    ----------
    fitters : list of ravest.fit.Fitter
        List of fitted Fitter objects
    names : list of str, optional
        Names for each model (default: Model 1, Model 2, ...)
    **kwargs
        Additional arguments passed to compute_evidence
        
    Returns
    -------
    dict
        Dictionary with model names as keys and (evidence, evidence_std) as values
    """
    if names is None:
        names = [f"Model {i+1}" for i in range(len(fitters))]
    
    if len(names) != len(fitters):
        raise ValueError("Number of names must match number of fitters")

    # TODO definitely need to read up on log variance etc in the paper    
    results = {}
    for name, fitter in zip(names, fitters):
        ln_evidence, ln_evidence_std = compute_evidence(fitter, **kwargs)
        results[name] = (ln_evidence, ln_evidence_std)
        # ln_evidence_std is always a tuple (lower_bound, upper_bound)
        print(f"{name}: ln(Z) = {ln_evidence:.2f} +{ln_evidence_std[1]:.2f}/{ln_evidence_std[0]:.2f}")

    return results