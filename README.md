# Prymer

## Introduction

Prymer is a Python library for Python-native data templating.
The intent is to make (for instance) large-scale remaps easy, clear, and
declarative up-front without even necessarily having the source data
already available. 

## Usage

At a small scale:

```python
import prymer

sample_src = {
    "list_of_numbers": [0,1,2],
    "some_string": "hello world"
}

get_first_number = prymer.Get['list_of_numbers'][0]
first_number = get_first_number(sample_src)  # returns 0
```

`prymer.Get` allows you to compose an access of an object or Python-native
data type using Python's own syntax into its own callable. You then call
the resulting callable on the source structure to extract the desired value.

At a larger scale, `prymer.port` can be used to resolve more complex
structures, to an extent. Consider this example:

```python
import prymer

sample_src = {
    "group_1": [
        {
            "user": "root",
            "name": "root",
            "uid": 0,
            "gecos": "ya rasputin"
        }
    ],
    "group_2": [
        {
            "user": "andy",
            "name": "andy",
            "uid": 1337,
            "gecos": "is the best"
        }
    ]
}

map_template = {
    "first_group1_username": prymer.Get['group_1'][0]['user'],
    "first_group2_gecos": prymer.Get['group_2'][0]['gecos']
}

# {'first_group2_gecos': 'is the best', 'first_group1_username': 'root'}
final_map = prymer.port(sample_src, map_template)
```

`prymer.port` will iterate through the template, look for any callables and
call them with the source map as the sole argument to fill out their values.

## Gotchas

Interfaces and functionality subject to change (this is a very new library).

`prymer.Get` does not, by default, protect against the source data not 
matching the provided specification; there are ways to prevent this, but
unfortunately they're a bit ugly. In the case of dicts and arrays, we can
do this:

```python
arr = [0,1]
get_third = prymer.Get[prymer.KeyOrDefault(2, None)]
# None
third = get_third(arr)
```

For attributes, we can't really use the attribute syntax directly nor can we
use Python's built-in getattr necessarily, but we can access them via the 
square bracket syntax and specify a default there:

```python
class someObj(object):
    pass

a = someObj()
c = someObj()
c.b = "yes b!"

get_attr_b = prymer.Get[prymer.FromAttr("b", "no b!")]
# This will be "no b!"
attr_b1 = get_attr_b(a)
# This will be "yes b!"
attr_b2 = get_attr_b(c)
```

You will also need to use the square bracket syntax and `FromAttr()` in cases
where you actually need to access the following attribute names:
`_GetChainLink__op`, `_GetChainLink__op_arg`, or `_GetChainLink__parent` since
these are "private" attributes -- see [Python's documentation on private
variables and class-local references](https://docs.python.org/2/tutorial/classes.html#private-variables-and-class-local-references) for more details.

Otherwise, in general, the exceptions that could be thrown should be the exact
same as if you attempted them directly on the accessed object proper, since
prymer attempts to use those same mechanisms where it can (so AttributeErrors
when attributes don't exist, IndexErrors where the index is out of bounds,
KeyErrors where a key doesn't exist, etc). 