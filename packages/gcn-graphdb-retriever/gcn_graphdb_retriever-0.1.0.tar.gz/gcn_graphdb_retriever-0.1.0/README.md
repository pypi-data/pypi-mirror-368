# GCN-GRAPHDB-RETRIEVER-MAIN
以下是关于GCN-graphdb-retriever的介绍
|方法|描述|
|:--:|:--:|
|subject_pipeline|提取GCN相关信息|
|gcn_graph_builder|构建知识图谱|

## 使用方法讲解
### 通过pip安装
<pre>
pip install GCN-Graphdb-Retriever
</pre>
### 1.直接在代码中进行应用
<pre>
from gcn_graphdb_retriever import subject_KEE_pipeline
from gcn_graphdb_retriever import gcn_graph_builder

def main():
    in_filepath = "tests/archive.txt.tar.gz"
    out_filepath = "tests/model_test.txt"
    examples_filepath = "tests/subject_parser_examples.json"
    model = "qwen3:14b"
    silent_errors = False
    examples_num = 1
    subject_KEE_pipeline.subject_pipeline(in_filepath, out_filepath, examples_filepath, model, silent_errors, examples_num)

    in_filepath = "tests/model_test.txt"
    silent_errors = False
    gcn_graph_builder(in_filepath, silent_errors)

if __name__ == "__main__":
    main()
</pre>

### 3.通过命令行调用
<pre>
ps@ps:~/桌面/Vscode_test/gcn-graphdb-retriever-main(1)/gcn-graphdb-retriever-main$ uv run subject_KEE_pipeline -i tests/archive.txt.tar.gz -o tests/model_test.txt --examples tests/subject_parser_examples.json
</pre>