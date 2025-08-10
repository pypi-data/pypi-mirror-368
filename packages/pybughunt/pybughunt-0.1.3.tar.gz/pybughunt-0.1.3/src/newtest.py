from pybughunt import CodeErrorDetector

detector = CodeErrorDetector()
code = '''
def example():
    print("Hello World;
    
'''
results = detector.analyze(code)
print(results)
