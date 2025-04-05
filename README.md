# URL Checker (Headless)

This script processes a CSV file containing approximately 30,000 URLs to identify which web pages contain relevant data. It is optimised for headless execution in cloud environments and is structured to avoid detection by bot-protection mechanisms.

## Overview

Many of the URLs point to pages that, even when valid, return a visible browser page with the message:

> **"The Graded Stakes Profile you were searching for could not be found"**

This message indicates that the page does not contain the data of interest, even though the page technically loads. The script checks each URL in the input CSV file, scans the page content for this specific error message, and records whether the page contains relevant data.

- If the error message is found → the script records `"no"` in the output CSV.
- If the message is not found → the script records `"yes"`, indicating the page may contain useful data for further inspection.

## Files

- `Equibase_URLS.csv`: Master input file containing ~30,000 URLs to be checked.
- `generate_cookies.py`: Script to generate cookies from a browser session.
- `test_cookies.py`: Script to test whether cookies can be used successfully to bypass bot detection.
- `url_checker_HEADLESS.py`: Main script that performs headless browsing, checks each URL for the error message, and saves the result as `"yes"` or `"no"`.

## Features

- Headless Chrome browsing with Selenium.
- Randomised user agents to reduce detection likelihood.
- Support for injecting session cookies (`cookies.pkl`).
- CSV splitting and batch processing to handle large volumes efficiently.
- Random delays between batches to simulate human-like browsing.
- Manual captcha mode if required.


## Output

- For each URL, the output CSV will contain:
  - The original URL.
  - A `"yes"` or `"no"` label indicating whether relevant data is present on the page.

Example results:  
![image](https://github.com/user-attachments/assets/06ebc592-17df-4e43-8382-d783e558d269)
