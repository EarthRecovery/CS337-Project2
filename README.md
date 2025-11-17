This is repository for CS337 lab2

## TO RUN:

- **Python 3.10**: Required Python version.
- **Conda** (for Conda installation) and **Pip** (for pip installation): Package managers.

## STEPS:

- (if needed) Create environment

  ```bash
   conda create -n <name> python=3.10
   ```

-  Activate environment

   ```bash
   conda activate <name>
   ```

- Install all requirements

   ```bash
   pip install -r requirements.txt
   ```

- Download the SpaCy language model `en_core_web_sm`:

    ```bash
    python -m spacy download en_core_web_sm
    ```