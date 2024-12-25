# ComiPy - Python 漫画管理器

ComiPy 是一个由 Python 编写的漫画管理器，旨在简化漫画文件的管理和查看。该工具支持上传压缩的 ZIP 文件格式的漫画，并通过一个直观的 Web 页面进行浏览。其特性包括：

- 支持上传并处理 ZIP 打包的漫画文件
- Web 界面查看漫画
- 实时生成压缩后的 WebP 图像进行传输，优化加载速度

## 功能

- **漫画上传**：上传 ZIP 格式的漫画文件，自动解压并展示。
- **Web 浏览**：通过简单易用的 Web 页面查看漫画内容。
- **图像压缩**：实时将图像转换为 WebP 格式，以减少加载时间并提升用户体验。

## 安装

### 先决条件

- Python 3.8 或更高版本
- 必须安装 `pip` 包管理工具

### 安装步骤

1. 克隆本仓库：

   ```bash
   git clone https://github.com/Kakune55/ComiPy.git
   cd ComiPy
   ```

2. 创建虚拟环境并激活（可选）：

   ```bash
   python -m venv .venv
   source venv/bin/activate  # Linux/MacOS
   venv\Scripts\activate  # Windows
   ```

3. 安装所需依赖：

   ```bash
   pip install -r requirements.txt
   ```

## 使用方法

1. 启动 Web 服务：

   ```bash
   bash app_control.sh start
   ```

   默认情况下，Web 服务会在 `http://127.0.0.1:8080` 启动。

2. 打开浏览器并访问 `http://127.0.0.1:8080`，即可上传和浏览漫画。

## 配置文件

1. 项目自带了一个模版配置文件 `app_d.ini`，使用时需要复制一份并重命名为 `app.ini`。
2. `app.ini` 文件中包含以下配置：

以下是 `app_d.ini` 配置文件的说明：

### [server] 部分
- **port=8080**: 服务器监听的端口号为 8080。
- **debug=0**: 是否开启调试模式，0 表示关闭，1 表示开启。
- **host=0.0.0.0**: 服务器绑定的主机地址，0.0.0.0 表示监听所有可用网络接口。
- **threaded=0**: 是否启用多线程处理请求，0 表示关闭，1 表示开启。

### [user] 部分
- **username=admin**: 用户名，默认为 admin。
- **password=admin**: 密码，默认为 admin。建议在生产环境中修改此密码以增强安全性。

### [database] 部分
- **path=./data/metadata.db**: 数据库文件路径，相对路径为当前目录下的 `data` 文件夹中的 `metadata.db` 文件。

### [file] 部分
- **inputdir=./input**: 输入文件夹路径，用于存放输入文件。
- **storedir=./data/file**: 存储文件夹路径，用于存放处理后的文件。
- **tmpdir=./data/tmp**: 临时文件夹路径，用于存放临时文件。

### [img] 部分
- **encode=jpg**: 图片编码格式，默认为 jpg 支持(jpg/webp)。
- **miniSize=400**: 图片的最小边长，默认为 400 像素。
- **fullSize=1000**: 图片的最大边长，默认为 1000 像素。


## 贡献

欢迎贡献！如果你有任何想法或建议，欢迎提交 Issue 或 Pull Request。

## 许可

该项目遵循 MIT 许可证 - 详情请参见 [LICENSE](LICENSE) 文件。