Implementation of Rubik's cube moves

To install it, run `pip install rubik_impl`

Usage:
```python
import rubik_impl
cube = rubik_impl.Cube()
cube.U() # apply a U move on the cube
cube.Ui() # apply Ui move
cube.apply("R U Ri Ui") # apply an algorithm on the cube
print(cube) # show the cube
```


