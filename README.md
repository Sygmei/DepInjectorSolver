# POMDepIn

> Python Orderly & Minuscule Dependency Injector

This is a very simple dependency injection framework for Python, heavily inspired by FastAPI system but without any dependencies.

## Example

```python
def requires_ten() -> int:
    print("Resolve requires_ten")
    return 10

def requires_twenty(ten: int = depends(requires_ten)):
    print("Resolve requires_twenty")
    return ten * 2

def requires_twenty_plus_a_plus_b(a: int, b: int, twenty: int = depends(requires_twenty)):
    print("Resolve requires_twenty_plus_a_plus_b")
    return twenty + a + b

def requires_multiple(
    a,
    b,
    complex: int = depends(requires_twenty_plus_a_plus_b),
    ten1: int = depends(requires_ten),
    ten2: int = depends(requires_ten),
    twenty1: int = depends(requires_twenty),
    twenty2: int = depends(requires_twenty)
):
    print("Resolve requires_multiple", a, b, complex, ten1, ten2, twenty1, twenty2)
    return a + b + complex + ten1 + ten2 + twenty1 + twenty2

def main():
    result = resolve_dependencies(requires_multiple, a=50, b=30)
    print(result)

if __name__ == '__main__':
    main()
```
