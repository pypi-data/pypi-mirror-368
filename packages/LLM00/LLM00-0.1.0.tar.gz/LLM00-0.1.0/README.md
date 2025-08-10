# LLM00

## Quick Start (忙しい人のためのLLM00)
```python
import LLM00

response = LLM00("What's the capital of France?")
print(response)  # -> "The capital of France is Paris."
```

## 概要 (Overview)
LLM00は、最小限のコードでLLM（Large Language Model）を呼び出し、応答を得ることができる非常にシンプルなツールです。従来、LLMを使う際には複雑なコードや設定が必要なことが多く、開発者にとって手間がかかるものでした。LLM00は、そうした手間を取り除き、簡単かつ迅速にLLMを活用できる環境を提供します。「LLM00」という名前の「00」は、扱う労力がほとんどゼロに近いことを象徴しています。

LLM00を使うことで、実装にかかるストレスを大幅に軽減し、開発者のモチベーションや生産性を向上させることが期待できます。

LLM00 is a tool designed to make the use of Large Language Models (LLMs) remarkably simple with minimal code. Traditionally, working with LLMs involves complicated setups and code, which can be a burden on developers. LLM00 eliminates this hassle, allowing for quick and easy integration of LLMs. The "00" in the tool’s name signifies the minimal effort required to utilize it.

By using LLM00, developers can significantly reduce the stress of implementation, enhancing both motivation and productivity.

## 特徴 (Features)
- **極めてシンプルなインターフェース (Extremely Simple Interface):**  
  1行のコードでLLMを呼び出して応答を取得できます。コードの読みやすさや記述の短さを徹底的に追求しています。
  
- **呼び出しの簡易化 (Simplified Call Process):**  
  従来のLLM呼び出しは設定やAPIの詳細な記述が必要でしたが、LLM00はそれらを自動化し、ユーザーが最小限の操作でLLMを扱えるようにしています。

- **軽量かつ効率的 (Lightweight and Efficient):**  
  LLM00は、動作に必要な設定を削減し、軽量なインターフェースでスムーズな実行を可能にします。

- **今後の機能拡張予定 (Future Functionality):**  
  現在、APIキーのファイルパスを自由に指定する機能が開発中です。将来的には、より柔軟な設定が可能となる予定です。

### 英語版:
- **Extremely Simple Interface:**  
  With just one line of code, users can call an LLM and get a response. The tool is designed with a focus on ease of readability and conciseness in coding.
  
- **Simplified Call Process:**  
  Traditional LLM calls require extensive configuration and detailed API setup, but LLM00 automates much of that, allowing users to handle LLMs with minimal steps.

- **Lightweight and Efficient:**  
  LLM00 reduces the necessary configurations to the bare minimum, offering a smooth, lightweight interface for efficient execution.

- **Future Functionality:**  
  A feature to freely specify the file path for API keys is currently under development, promising more flexibility in future updates.

## インストール (Installation)
LLM00をインストールするには、以下のコマンドを実行します。

```bash
pip install LLM00
```

To install LLM00, simply run the following command:

```bash
pip install LLM00
```

## 使い方 (Usage)
LLM00を使ったLLM呼び出しは非常に簡単です。以下のコード例を見てください。

### コード例 (Code Example)
```python
import LLM00

print(LLM00("ずばり簡潔に、タコの足は何本？"))  # -> "8本です。"など、AIの返答が文字列で返る
```

Calling an LLM using LLM00 is extremely straightforward. Here's an example:

```python
import LLM00

print(LLM00("Simply put, how many legs does an octopus have?"))  # -> "It has 8 legs." (or similar response)
```

このコードでは、`LLM00`に簡単な質問を渡すだけで、LLMが自然言語で答えてくれます。APIキーや複雑な設定を意識する必要はありません。

## 注意事項 (Notes)
- **APIキーの設定 (API Key Setup):**  
  現在のバージョンでは、APIキーのファイルパス指定は固定されています。柔軟にAPIキーを指定する機能は、将来的にリリース予定です。

- **API Key Setup:**  
  In the current version, the API key file path is fixed. The ability to specify a custom API key path is planned for future updates.

## 今後のアップデート予定 (Upcoming Updates)
- **APIキー管理機能の拡充:**  
  より自由度の高いAPIキー設定機能が開発中です。
  
- **設定オプションの追加:**  
  環境やユースケースに合わせてカスタマイズできる設定オプションの拡充が予定されています。

- **Expanded API Key Management:**  
  A more flexible system for setting API keys is currently under development.
  
- **Additional Configuration Options:**  
  Planned updates will introduce more customization options tailored to specific environments and use cases.
