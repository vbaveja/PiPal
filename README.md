# PiPal

PiPal is an AI-assisted Raspberry Pi learning companion for kids and beginner makers.

The goal of PiPal is to help students turn ideas into real projects through curiosity, experimentation, and guided learning.

## Local virtual environment

PiPal uses a local Python virtual environment for development. This folder is not committed to Git so each person can create it on their own machine.

Create it locally with:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

If you do not have a requirements file yet, install the packages you need for your current work and keep the environment local to your machine.

If you want, you can also add a `requirements.txt` later so the setup is easier to repeat.

## Admin reference

For local documentation and reference, the current demo admin unlock password used in the Streamlit app is:

- `pipal-admin`

This password is hardcoded in `frontend/app.py` for the local demo setup.