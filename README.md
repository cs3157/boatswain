Boatswain
=========

> Follow the river and you will find the C.

##### **boatswain** _noun_
> a ship's officer in charge of equipment and the crew

A collection of command-line course management scripts used by Columbia CS TAs.
Primarily targets interfacing with Columbia's LMS, [Canvas][canvas], but over
time we will also add scripts that will support interfacing with GitHub.

[canvas]: https://github.com/instructure/canvas-lms


Getting Started
---------------

Let's install all the dependencies the right way.

Make sure you have Python3 and [`virtualenv`][venv] installed. Clone this repo.
In the repo directory, create a virtual environment with the following command:

    $ virtual venv

`venv` could have been any path name, but we're going to assume that you used
`venv`, and proceed. You should see a directory named `venv` created, and now
you can activate this virtual environment whenever you want. Assuming you're
using Bash:

    $ . venv/bin/activate

Your shell prompt should now have `(venv)` in front of it. Check to make sure
that your `python` verion is 3, not 2.

Now, you can install dependencies into this virtual environment.

    (venv) $ pip install -r requirements.txt

This installs all the dependencies from the `requirements.txt` file.

You're all set! If you'd like to exit your virtual environment, you can run
the command `deactivate` at any time. Just make sure to activate it again any
time you're using Boatswain.

[venv]: https://virtualenv.pypa.io/en/stable/


Authenticating with Canvas
--------------------------

In order to interface with the Canvas API, one must generate an authentication
token from Canvas. This can be done in the Settings panel, in the Approved
Integrations section. Click "New Access Token", specify a legitimate purpose,
and optionally an expiration date. The next dialogue will display a generated
string that will act as your authentication token.

_Be sure to save the authentication token somewhere safe! It can't be recovered
from Canvas once the dialogue is closed._

You'll use this to set up your Boatswain config file.

Authenticating with GitHub
--------------------------

Similarly, you can generate an authentication token from GitHub. For now, no
published scripts actually use this, so you can only do this if you really want
to. It's not at all difficult to just add in or change the token yourself later.


Setting up your Boatswain configuration
---------------------------------------

Boatswain is improves upon a previous tool (Canvas Wrangler) in that it actually
uses a configuration file like a responsible sailor is supposed to. By default,
this file is located at `~/.boatswain.ini`. It uses the `.ini` file because
nostalgia.

To set it up, you can actually just run the `boatswain_env.py` mini-library.
It will take you through an interactive series of steps that will populate a
minimal Boatswain configuration:

    (venv) $ ./boatswain_env.py

Boatswain will be expanded to support arbitrary arguments in this config file
which could save you some typing when running commands, but for now just accept
that it's a little overkill.


Canvas Wrangler
===============

> Dear CourseWorks,
> 
> I am so so sorry that I made fun of you and called you names.  
> I called you CourseSucks all the time.  
> I take it back.  
> 
> You are air.  
> You are water.  
> I never thought about what would happen to me if you left.  
> I am going to cling to you as long as I can.  
> I love you.
> 
> Jae

This is the [predecessor][cw] to Boatswain, so we updated it with a few small
improvements.

In a nutshell, Canvas Wrangler automates the grade upload process from a CSV
spreadsheet to a Canvas assignment. This is great if you graded homework
submissions elsewhere and would like to push your grades to Canvas for students
to see. It supports numerical grades and textual comments.

You can start by seeing the different options that the Wrangler supports:

    (venv) $ ./canvas-wrangler.py --help

[cw]: https://github.com/cs3157/canvas-wrangler

Grade Spreadsheet Format
------------------------

The grade spreadsheet should be a `.csv` file. Entries containing commas should
be wrapped in quotation marks (e.g. `"contains a comma, this entry"`), and
quotation marks should be "escaped" using double quotation marks
(e.g. `"this entry ""uses"" quotation marks"`).
(Exporting a .csv from Google Docs will do this for you.)

The grade spreadsheet must contain a single header row so that Canvas Wrangler
can calibrate its column indices. By default, Canvas Wrangler will expect the
student ID column to be named `uni`, the grade column to be named `grade`, and
the comment column to be named `comment`.

However, these can be overridden by using the `-S`, `-G`, and `-C` flags
respectfully and specifying the header name after the flag argument:

    (venv) $ ./canvas-wrangler.py -G studentgrade <other args...>

In this case, instead of looking for grades in a column with header `grade`,
the Wrangler will instead look for `studentgrade`. It will still look for
comments under a column with header `comment` and the student ID under a column
with header `uni`.

Extra columns are ignored.

You may also instruct the Wrangler to not upload grades or comments at all.
You do so by passing an empty string to `-G` or `-C`:

    (venv) $ ./canvas-wrangler.py -C '' <other args...>

In this case, the Wrangler will look for grades in a column with header `grade`,
but not submit any comments.

You cannot instruct the Wrangler not to submit either, nor can you pass it an
empty student ID header name.


Grade and Comment Submission
----------------------------

In order to upload grades to a Canvas assignment, you must retrieve its course
ID and its assignment ID.

-   The course ID is the last portion of the course page's URL. For example, in
    [https://courseworks2.columbia.edu/courses/6858](https://courseworks2.columbia.edu/courses/6858),
    the course ID is 6858.

-   The assignment ID is the last portion of the assignment page's URL. For example, in
    [https://courseworks2.columbia.edu/courses/6858/assignments/25314](https://courseworks2.columbia.edu/courses/6858/assignments/25314),
    the assignment ID is 25314. Note that before `/assignments/<assignment-id>`
    also comes the course ID.

The program updates each student's grade record by reading the from the grades
CSV spreadsheet and creating a new form entry for each comment and grade with
their student ID.

To upload grades, run the command (with additional options):

    (venv) $ ./canvas-wrangler.py <course-id> <assignment-id> <grades.csv-path>

If it succeeded, it will give you a URL which you can use to check up on the
grade upload process. It can usually take a few minutes to process all the
grade submissions.

This should work even if the student has not uploaded and submitted any files
for the assignment on Canvas. If the student is missing from the Canvas roster,
the grade upload status will let you know, but the rest of the grades will
continue to be processed, so if you're managing multiple sections, you can just
upload the same spreadsheet to two separate assignments in separate courses.

_The assignment must be published before grades and comments can be uploaded._
It's also a good idea to mute the assignment before pushing grades. Keep in mind
that grades will overwrite, but comments will stack (previous comments will
still be visible to students unless you go and manually delete them).

If you'd like to run the Wrangler without actually submitting anything, you can
pass it the `-n` flag. This will prevent it from actually performing the POST
request that submits the grades. If you would like additional output to help you
debug any problems, pass the Wrangler the `-v` flag for verbose output.


Other Remarks
-------------

If you have any suggestions/complaints/_love letters to the old Courseworks_,
please feel free to leave an Issue on this GitHub repo, or contribute by issuing
us a Pull Request!
