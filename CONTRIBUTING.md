# Contributing to TEDx-YTT
We love your input! We want to make contributing to this project as easy and transparent as possible, whether it is:

- Reporting a [bug](#report-bugs-using-githubs-issues)
- Discussing the [current state of the code](Discussing-the-current-state-of-the-code)
- Submitting a [fix](#Submitting-a-fix)
- Proposing [new features](#proposing-new-features)

## Our development process
We use GitHub to sync code, to track issues and feature requests, as well as accept pull requests.
Pull requests are the best way to propose changes to the codebase (we use [Github Flow](https://guides.github.com/introduction/flow/index.html)). 

We actively welcome your pull requests
- Improving current code (fixing issues, improving PEP-8 compability)
- Improving documentation
- Fixing issues
- Proposing new features

For all your pull requests, please note that:
- For the python code base we aim to be as PEP-8 consistent as possible. Please check your code before submitting.
- We use docstrings to document functions and objects. If you add parameters or returns, adjust existing docstrings.
- Update the README.md, if necessary.
- For additional scripts to analyze/graph data please use a new folder within the main repo.

## Report bugs using Github's [issues](https://github.com/briandk/transcriptase-atom/issues)
We use GitHub issues to track public bugs. Report a bug by [opening a new issue](); 

**Great Bug Reports** tend to have:

- A quick summary 
- Steps to reproduce
  - Be specific!
  - Give sample code if you can.
- What you expected would happen.
- What actually happens.
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work).
- log.log file and date & time of the occurence of the issue (if you turned logging on).

## Discussing the current state of the code
Please use a pull request to discuss the current state of the code and if you have suggestions to improve it.

## Fixing issues
Please make sure that the code runs smoothly with all combinations of paramteres (especially combinations of -u True/False and -s True/False). We have not (yet) implemented automatic testing so be very careful your fix does not introduce new issues!

## Proposing new features
Please use a pull request to suggest new features even if you have not implemented them yet or need help completing the new feature.


## Any contributions you make will be under the MIT Software License
In short, when you submit code changes, your submissions are understood to be under the same [MIT License](http://choosealicense.com/licenses/mit/) that covers the project. When your pull request is merged, you will be added to the list of authors.

## References
This document was adapted from the open-source contribution guidelines for [Facebook's Draft](https://github.com/facebook/draft-js/blob/a9316a723f9e918afde44dea68b5f9f39b7d9b00/CONTRIBUTING.md)
and [BrianDk's](https://gist.github.com/briandk/3d2e8b3ec8daf5a27a62#file-contributing-md) adjustments to it.
