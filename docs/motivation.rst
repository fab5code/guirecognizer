Motivation
==========

Automation can be done in many ways, but GUI-based automation ie interacting with the screen, mouse, and keyboard,
is often the simplest starting point for small to moderately complex bots.
*guirecognizer* was created to make this process faster, more reliable, and easier to iterate on.

GUI-based bots
--------------

GUI-based bots automate applications by relying exclusively on what is visible on the screen,
using pixel data together with mouse and keyboard input.
This approach contrasts with deeper integrations such as browser automation or programmatic APIs.

This model has clear strengths:

- **Universality**: any application that can be used by a human can be automated, without access to internal APIs or tooling.
- **Low setup cost**: for simple or moderately complex bots, working directly from the screen can be faster than introducing dedicated automation frameworks.

It also comes with unavoidable drawbacks:

- **Fragility**: changes in resolution, UI layout, colors, or animations can break recognition.
- **Lower performance** and reliability compared to APIs or dedicated softwares.

GUI-based automation is therefore a pragmatic choice. It trades robustness and performance for generality and ease of use.
The goal of *guirecognizer* is to reduce the friction when defining, testing and updating visual interactions.

Other GUI-based automation libraries
------------------------------------

Many libraries help build GUI-based bots by recognizing patterns on the screen and controlling the mouse and keyboard.
In most cases, the recognition logic is tightly coupled with the bot behavior, so any change in the GUI can require rewriting parts of the bot.
They often rely on limited strategies, such as image matching, forcing the user to manage large sets of reference images for each visual element.
As the number of elements grows, maintaining these resources becomes cumbersome,
and testing recognition typically requires running the bot, making feedback slow and debugging tedious.

How guirecognizer simplifies GUI automation
-------------------------------------------

*guirecognizer*, together with :doc:`guirecognizerapp <app>`, separates recognition from bot logic, making it easier to define, test
and update visual interactions without rewriting the bot.
Actions and preprocessing steps are configured independently and their results can be previewed instantly in the application,
providing fast feedback and reducing iteration time.
This approach minimizes resource management overhead, avoids tightly coupling recognition with behavior, and allows pipelines of actions to be composed visually.

Limitations remain inherent to GUI-based automation: recognition can still break with major UI changes
and performance is lower than API-driven automation.
*guirecognizer* focuses on rapid, maintainable prototyping and reliable iteration rather than replacing high-performance or fully robust automation solutions.
