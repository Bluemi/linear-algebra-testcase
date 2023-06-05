# linear-algebra-testcase
A small utility program in Python (pygame + numpy) to visualize concepts of linear transformations.
View [3Blue1Brown](https://www.youtube.com/watch?v=kYB8IZa5AuE) for a nice introduction.


## Installation
```bash
# clone repository
git clone https://github.com/Bluemi/linear-algebra-testcase.git
cd linear-algebra-testcase

# install requirements (numpy, pygame)
pip3 install -r requirements.txt

# run the programm
python3 ./src/main.py
```

Consider using a virtual python-environment (eg [virtualenvwrapper](https://pypi.org/project/virtualenvwrapper)).

## Usage
You can move around in the plane with the mouse. Zoom is controlled with the mouse wheel.
If you click on the button on the left top, a menu opens.

The menu shows three sections:
- **Object:** You can have two kinds of objects: A single vector or a collection of vectors ordered in a circle (or ellipse, if modified). Add these objects by clicking on the plus buttons. You can change the values of a vector by dragging them in the coordinate system.
- **Transforms:** Here you can add Transformation matrices. The first plus-button creates a two-dimensional matrix. If you want to utilize translation as well you have to use the second plus-button to create a three-dimensional transformation matrix. These matrices are not rendered directly, but can be later used for transformations. To change the values of a matrix, hold an element of the matrix and move the mouse up or down. The bottom row of a 3 dimensional matrix does not change anything (as long as you dont use it for later transformations).
- **Transformed:** If you want to see the effect of your Transforms use this section. The first button creates a transformed version of one of your objects.
                   To select an object click on the created transform and then on the left side on one of the objects. Then click on the transformed again and click on the transformation you want to use.
                   This only works for two dimensional transformation matrices (WIP).
                   The last add button creates a custom-transformation. If you click on the custom transformation a window will pop up, that enables you to write python code.
                   See [Custom Transformed](#custom-transformed) for more information. To close the window press `Esc`. You can remove the last sign with `Backspace` and everything with `Del`.
                   As you can see, this editor is very rudimentarily (no removal/edit of signs that are not the last sign).

### Controls
- To remove any object, transform or transformed hover over the element in the menu on the left side and press `Del` or `Backspace`.
- You can toggle between render mode `LINE` and `POINT` by hovering over an rendered element on the left side and pressing `r`.


### Custom Transformed
If you create a custom transformed and click on it, a text window appears. Here you can write a python expression.
You can use all object names listed above and numpy functions (accessible via `np`). Objects from above will be presented as [numpy-ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html).

**Example:** Lets say you have a vector `v1` and a 2d transformation matrix `T1`. You could write `T1 @ v1` to apply the transformation matrix on your vector and render the result.
The same works for unit circles (replace `v1` with `u1`).

As applying a 3d transformation matrix on a 2d vector is a bit complicated, you can use the special function `mm()`(matrix-multiplication): `mm(T1, v1)`.

## Limitations / Risks
- To evaluate custom-transformations the python builtin `eval()` is used, which allows arbitrary code execution. For example you could use `exit()` as formula to end the program. So be a bit careful.
- The first kind of transformated-objects is not supported for 3d-transformation matrices (WIP).
- The formula editor is very limited. No cursor position and only very basic editing possibilities.
- Many more...
- The code is in a horribly shape. Maybe I will find time to tidy up a bit. Probably not...
