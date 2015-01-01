> I wrote this in June 2014 as a part of a 14000 char Markdown doecument for self-reference, before I took a long break from the project.

------

### Managers
Each "stage" in the translation process is managed by their own separate Managers.

Managers do not work with/on the data-structures directly, instead they manage the lower-level classes that work on the data-structures. This allows for multiple levels of abstractions of the Translation process. Think of what Classes and functions/methods are for a program, that's what Managers and lower-level classes are to the Translation process.

Every Manager has options which can be modified. The lower level classes use these options and the data passed to them to do their work.

Currently there are 5 managers:

  1. PreProcessingManager:
    - Manages the pre-processing of the code and the building of the AST.
  2. AnalysisManager:
    - Manages the process of analysis of the AST to figure out what all the code does and builds and populates the VariableMap.
  3. ModifiersManager:
    - Manages AST modification based on the information collected by the Analyser.
  4. CodeGenerationManager:
    - Manages the final stage of code-generation to convert the optimised and "translated" AST into optimised C++ code.
  5. TranslationManager:
    - Manages the entire translation process. Like the boss of a company, the TranslationManager manages all the processes and does its best make the system perform optimally.

A description of how the specific manager manages it's "staff" is given wherever the manager is at work.

Now that you know a bit about how everything happens on the super-high level, let's talk about what we were here for...

## What's the story behind the Translation?
> Before I get to it, please note that I wrote this full section as a story of how stuff works at a company called "Py2C"... A company that specializes in source-to-source translation.

------

[cropped]
<!-- Each file made is essentially a data-structure. -->
A request is sent to the TranslationManager by the customer to translate some code. Once the code clears the his basic checks, the TranslationManager passes this code to the PreProcessingManager who is instructed to make a file named AST, which can be used to track the changes as this code translation proceeds. The PreProcessingManager now gets his department working.

According to a the companies protocols, if at any point of time there is a problem while working with the data given to a Manager by the TranslationManager, the Manager is to report the same to the TranslationManager who has to then inform the customer that they couldn't complete the translation due to the above problem.

Following all the company protocols like all other managers in the company, the PreProcessingManager ends up submitting the completed file to the TranslationManager.

The TranslationManager makes a magic-copy of the AST which gets modified whenever the AST is modified and keeps the magic-copy with himself. He then passes the AST to the AnalysisManager. The AnalysisManager gets his department working to figure out as much as they can about the control flow and add that information in the AST file. He also makes them find out everything they can about the variables in the AST and puts that into a new file named VariableMap. AnalysisManager returns the AST with extra information added and all variable information collected stored in VariableMap to the TranslationManager.

TranslationManager now passes the AST and VariableMap over to the ModifiersManager who makes his department make changes to the AST file based on the VariableMap. He then returns the changed AST file and the unchanged VariableMap back to the TranslationManager.

TranslationManager now takes a look at the file, looking for obvious flaws and then passes the file over to CodeGenerationManager who generates a final report and submits it to TranslationManager who gives it to the customer.

Phew!! Now, if there's a problem with the final report, the report and original file should be submitted to me, by the user... Right? :laughing:
