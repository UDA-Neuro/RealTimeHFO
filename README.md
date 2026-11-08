# RealTimeHFO

Standalone Python research detector for **80–250 Hz ripple candidates** in
completed or growing 10 kHz BESA ECoG recordings. It can also read 1 kHz NPZ
files for synthetic testing. No MATLAB, BCI2000, GPU, or cloud service is
required.

## Run

On Windows, install Python 3.12, then from this repository:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -m realtimehfo
```

The GUI chooses a BESA/NPZ file, results folder, start, duration, and saved-file
or growing-file mode. Double-click `Start-RealTimeHFO.cmd` after installation.
For command-line analysis of the first five minutes:

```powershell
python -m realtimehfo --input 'D:\data\recording.besa' --output-dir results
```

For a recording that is being written, use `--follow`. The detector waits for
committed BESA blocks, processes each five-second span after 0.5 seconds of
right-hand context becomes available, and appends events to a CSV. Press
Ctrl+C to stop the CLI, or **Stop** in the GUI. A finite follow duration can
be set with `--duration 300`; otherwise it continues until stopped.

## Detector and output

The BESA signal is antialias resampled to 1 kHz with a fixed 301-tap Kaiser
FIR. A fourth-order zero-phase Butterworth filter selects 80–250 Hz. A 5 ms
moving RMS envelope is screened at its mean + five standard deviations.
Intervals exceeding the threshold are joined across gaps of at most 10 ms.
An accepted interval lasts 6–200 ms and contains at least four positive peaks
in the filtered signal. This detects **ripple-band candidates only**; it does
not detect 250–500 Hz fast ripples. Five-second processing spans use 0.5
seconds of filtering context; only peaks in the span's core are recorded.
Default channels exclude `DC01`-style auxiliary inputs; use `--include-dc` to
include them.

Each run writes `hfo-*.csv` with original channel number and label,
start/peak/end time in seconds, RMS score, and channel threshold. Its JSON
companion records the settings, selected channels, progress, and elapsed time.
A result is a **candidate**, not an expert-confirmed pathological HFO.
Bandpass ringing around spikes and artifacts can produce false positives;
the rate has not yet been measured against expert annotations.

The RMS threshold is inspired by
[Staba et al. (2002)](https://pubmed.ncbi.nlm.nih.gov/12364503/), but this
implementation uses an 80–250 Hz band and its own peak/duration criteria.
It should not be described as an exact implementation of that detector.

## Test

```powershell
python -m unittest discover -s tests -p 'test_*.py'
```

No patient recording is distributed in this repository. The BESA reader is
derived from [UDA-Neuro/RealTimeMI](https://github.com/UDA-Neuro/RealTimeMI)
under the MIT license; see [PROVENANCE.md](PROVENANCE.md).

