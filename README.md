# linear-algebra-testcase
A small utility program in Python (pygame + numpy) to visualize concepts of linear transformations.
View [3Blue1Brown](https://www.youtube.com/watch?v=kYB8IZa5AuE) for a nice introduction.


## Installation
- clone the repository
- install requirements (aktivate virtualenv)
```
# clone repository
git clone https://github.com/Bluemi/linear-algebra-testcase.git
cd linear-algebra-testcase

# install requirements (numpy, pygame)
# maybe create/activate a virtual python-environment before (https://pypi.org/project/virtualenvwrapper/)
pip install requirements.txt

# run the programm
python ./src/main.py
```

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
                   See [Custom Transformed](#custom-transformed) for more information. To close the window press `ESC`. You can remove the last sign with `backspace` and everything with `DEL`.
                   As you can see, this editor is very rudimentarily (no removal/edit of signs that are not the last sign).

### Controls
- To remove any object, transform or transformed hover over the element in the menu on the left side and press `DEL` or `Backspace`.
- To close the formular editor press `ESC`.
- You can toggle between render mode `LINE` and `POINT` by hovering over an rendered element on the left side and pressing `r`.


### Custom Transformed
You can use all object names listed above and numpy functions (accessible via `np`). 
**Example:** Lets say you have a vector `v1` and a 2d transformation matrix `T1`. You could write `T1 @ v1` to apply the transformation matrix on your vector and render the result.
The same works for unit circles (replace `v1` with `u1`). As applying a 3d transformation matrix on a 2d vector is a bit complicated, you can use the special function `mm()`(matrix-multiplication): `mm(T1, v1)`. This will automatically convert your vector `(x, y)` to a new vector `(x, y, 1)` apply the transformation matrix and then cut the last vector dimension again, to regain 2 dimensions.
