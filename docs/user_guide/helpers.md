# 🛠️ CoFmuPy Helper Scripts

CoFmuPy provides a set of **helper scripts** designed to simplify working with
**Functional Mock-up Units (FMUs)** and co-simulation workflows. These scripts offer
**debugging tools, model extraction utilities, and automation features** to enhance user
experience.

---

## 📜 Available Helper Scripts

| Script Name                                                                            | Description                                                                                               |
|----------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------|
| [`cofmupy-extract-fmu`](#extracting-fmu-information-with-cofmupy-extract-fmu)          | Extracts and displays all metadata from an FMU file. Optionally it should export information to csv file. |
| [`cofmupy-construct-config`](#constructing-config-file-with-cofmupy-construct-config) | Construct a configuration file from connections csv file and initializations csv file (optional).         |
| `User Interface`                                                                       | 🚧 *Coming soon...*                                                                                       |


## 📦 Extracting FMU Information with `cofmupy-extract-fmu`

The `cofmupy-extract-fmu` helper script is a command-line tool designed to **extract and
display (or export) all relevant information** from an FMU (Functional Mock-up Unit) file. It helps
users quickly inspect FMU metadata, including:

- **Inputs, outputs, and parameters**
- **Default values and variable types**
- **Integration step size**

This tool is particularly useful for **debugging, documentation, and ensuring FMU
compatibility** before running co-simulations.

---

### 📜 Usage
The `cofmupy-extract-fmu` script is executed from the command line with the following
syntax, output_file argument is optional:

```sh
cofmupy-extract-fmu <path_to_fmu_file> [--output_file file]
```

For example, if you have an FMU file named `model.fmu` in the current directory, run:

```sh
cofmupy-extract-fmu model.fmu
```

This will extract and display all the FMU metadata in a well-structured table.

For example, if you have an FMU file named `model.fmu` in the current directory,
and want to export information to extract_infos.csv file, run:

```sh
cofmupy-extract-fmu model.fmu --output_file ./extract_infos.csv
```

This will extract and export all the FMU metadata in extract_infos.csv file.


## 📦 Constructing config file with `cofmupy-construct-config`


The `cofmupy-construct-config` helper script is a command-line tool designed to **construct configuration file**. 

It helps users quickly create json formatted file, which is then usable for CoFmuPy co-simulation, from a csv formatted connection list.
Optional argument initialization list (csv formatted) should improve configuration file with initial configuration for fmus. 

Expected connections list format is csv (separator `,`), with a first label line columns below :

| Columns title | Column Description              |
|---------------|---------------------------------|
| from_path     | Path of the source fmu          |
| from_id       | Id of the source fmu            |
| from_name     | Expected name of the source fmu |
| from_var_name | Name of the source variable     |
| to_path       | Path of the target fmu          |
| to_id         | Id of the target fmu            |
| to_name       | Expected name of the target fmu |
| to_var_name   | Name of the target variable     |

Expected initializations list format is csv (separator `,`), with a first label line columns below :

| Columns title | Column Description                 |
|---------------|------------------------------------|
| Fmu_id        | Id of the concerned fmu            |
| Variable      | Name of the variable to initialize |
| Value         | Expected value of the variable     |


This tool is particularly useful for complex co-simulations (many connections) or complex fmus (many inputs/ouputs).

---

### 📜 Usage
The `cofmupy-construct-config` script is executed from the command line with the following
syntax, `initializations_file` argument is optional:

```sh
cofmupy-construct-config <path_to_connections_file> [--initializations_file path_to_initializations_file]
```

This will extract information from input files and create `config.json` file ready to use for co-simulations
execution with CoFmuPy.

Extracted file `config.json` should then be manually edited to manage cosimulation options, data stream or storage
