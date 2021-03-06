import argparse
import os
from pathlib import Path
from perf._bench import BenchmarkSuite
from jinja2 import Environment, FileSystemLoader

import seaborn as sns
import pandas as pd

sns.set(style="whitegrid")

parser = argparse.ArgumentParser(description='Convert a list of benchmarks into a set of PNG graphs')
parser.add_argument('files', metavar='N', type=str, nargs='+',
                    help='files to compare')
args = parser.parse_args()

benchmark_names = []
records = []
first = True
for f in args.files:
    benchmark_suite = BenchmarkSuite.load(f)
    if first:
        # Initialise the dictionary keys to the benchmark names
        benchmark_names = benchmark_suite.get_benchmark_names()
        first = False
    bench_name = Path(benchmark_suite.filename).name
    for name in benchmark_names:
        try:
            benchmark = benchmark_suite.get_benchmark(name)
            if benchmark is not None:
                records.append({
                    'test': name,
                    'runtime': bench_name.replace('.json', ''),
                    'stdev': benchmark.stdev(),
                    'mean': benchmark.mean(),
                    'median': benchmark.median()
                })
        except KeyError:
            # Bonus benchmark! ignore.
            pass

df = pd.DataFrame(records)
tests = []
for test in benchmark_names:
    # Draw a pointplot to show pulse as a function of three categorical factors
    
    g = sns.factorplot(
        x="runtime",
        y="mean",
        data=df[df['test'] == test],
        palette="YlGnBu_d",
        size=12,
        aspect=1,
        kind="bar")
    g.despine(left=True)
    g.savefig("png/{}-result.png".format(test))
    tests.append({
        'name': test,
        'results_table': df[df['test'] == test].to_html()
    })

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

j2_env = Environment(loader=FileSystemLoader(THIS_DIR),
                     trim_blocks=True)
result = j2_env.get_template('template.html').render(
    tests=tests
)
with open('index.html', 'w') as out_html:
    out_html.write(result)
