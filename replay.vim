python << EOF
import os
import sys
sys.path.append("/home/mboehm/repos/pylog")
import events
import logreader
import replay
import vim

stepper = None
def start_stepper(filepath):
    global stepper
    with open(filepath, "r") as log_file:
        reader = logreader.JsonFileEventReader(log_file)
        event_list = list(reader.iter_events())

    stepper = replay.Stepper(event_list)

def open_location(location):
    vim.command("edit {}".format(location.file))
    vim.command(str(location.line))
    vim.command("normal! zt")

def apply_locations(location_list):
    vim.command("new")
    vim.command("only")
    if location_list:
        open_location(location_list[0])
    for location in location_list[1:]:
        vim.command("botright vsp")
	open_location(location)
EOF

function! DoStep(step)
python << EOF
if stepper is None:
    vim.command('echoerr "call StartStepper(filepath) first!"')
step = vim.eval("a:step")

if step == "f":
    stepper.step_forwards()
elif step == "b":
    stepper.step_backwards()
elif step == "ov":
    stepper.step_over()
elif step == "ou":
    stepper.step_out()
elif step == "l":
    stepper.step_until_location(replay.Location(os.path.abspath(vim.current.buffer.name), vim.current.window.cursor[0]))
apply_locations(list(stepper.locations))
EOF
endfunction

function! StartStepper(filepath)
python << EOF
start_stepper(vim.eval("a:filepath"))
EOF
endfunction

function! StepForwards()
call DoStep("f")
endfunction
function! StepBackwards()
call DoStep("b")
endfunction
function! StepOver()
call DoStep("ov")
endfunction
function! StepOut()
call DoStep("ou")
endfunction
