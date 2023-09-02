# Blender-EasyAutomation
A simple addon to ease the automation and scripting workflow in blender.

![easyautomation promo](https://github.com/FScociety/EasyAutomation/assets/40910944/f4f22aff-6337-486c-a605-bbd994d5e1f2)

## Features

- Convenient list of all easyautomation scripts
- Batch runnning multiple script at once
- Quick access to text editor while staying in 3d view
- Easy variable exposing to the UI
- Global scripts that can be easily linked into every file

## EasyAutomation format

### What is an EasyAutomation script?
Every script, that starts with `#EA-Script` will be recognized by EasyAutomation

### Defining EA variables
- `#Global` : Exposes the variable, needed for every other EA syntax
- `#Seperator` : Closes the current UI box, so new variables are put into a new one 
- `#NoLine` : Combines the next variable and the current variable into a single line
- `#NoName` : Doesn't display the name of the variable, just the value
- `#NoValue` : Doesn't display the value of the variable, just the name (Can be used as a title)
- `= / :` : (=) Defines the default value of a variable (:) Defines the type of variable

Side by side example:

![scripting_syntax](https://github.com/FScociety/EasyAutomation/assets/40910944/f99e7c5c-ac6f-4316-9125-4584c94f57ee)

## Installation

1. Download the .zip from the green button
2. Blender -> Preferences -> Addons -> Install Addon
