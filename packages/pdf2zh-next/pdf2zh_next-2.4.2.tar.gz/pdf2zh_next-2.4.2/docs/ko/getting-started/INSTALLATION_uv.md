[**시작하기**](./getting-started.md) > **설치** > **uv** _(현재)_

---

### uv를 통해 PDFMathTranslate 설치하기

#### uv란 무엇인가요? 어떻게 설치하나요?

uv는 Rust로 작성된 매우 빠른 Python 패키지 및 프로젝트 매니저입니다.
<br>
컴퓨터에 uv를 설치하려면 [이 글](https://docs.astral.sh/uv/getting-started/installation/)을 참조하세요.

---

#### 설치

1. Python 설치 (3.10 <= 버전 <= 3.12);

2. 다음 명령어를 사용하여 패키지를 사용하세요:

    ```bash
    pip install uv
    uv tool install --python 3.12 pdf2zh-next
    ```

설치 후, **명령줄** 또는 **WebUI**를 통해 번역을 시작할 수 있습니다.

!!! Warning

    `command not found: pdf2zh_next` 오류가 발생하면 다음과 같이 환경 변수를 설정한 후 다시 시도해 주세요:

    === "macOS 및 Linux"

        ~/.zshrc 파일에 다음을 추가하세요:

        ```console
        export PATH="$PATH:/Users/Username/.local/bin"
        ```

        그런 다음 터미널을 재시작하세요

    === "Windows"

        PowerShell에서 다음을 입력하세요:

        ```powershell
        $env:Path = "C:\Users\Username\.local\bin;$env:Path"
        ```

        그런 다음 터미널을 재시작하세요

> [!NOTE]
> WebUI 사용 중 문제가 발생하면 [사용법 --> WebUI](./USAGE_webui.md)를 참조하세요.

> [!NOTE]
> 명령줄 사용 중 문제가 발생하면 [사용법 --> Command Line](./USAGE_commandline.md)를 참조하세요.

<div align="right"> 
<h6><small>이 페이지의 일부 내용은 GPT에 의해 번역되었으며 오류가 포함될 수 있습니다.</small></h6>