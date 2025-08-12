from setuptools import setup, find_packages

setup(
    name="pyaidrone",
    version="1.7",
    description="Library for AIDrone Products",
    long_description=open("README.md").read(),  # README.md 내용을 long_description으로 사용
    long_description_content_type="text/markdown",  # README 파일이 markdown 형식임을 지정
    author="IR-Brain",
    author_email="ceo@ir-brain.com",
    url="http://www.ir-brain.com",
    packages=find_packages(),  # find_packages()를 사용해 서브패키지까지 자동 탐색
    install_requires=[
        'pyserial>=3.4',
        'pynput>=1.7.3',
    ],
    classifiers=[  # 추가 메타데이터
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # 실제 라이선스를 설정해야 함
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',  # 최소 Python 버전 요구 사항 설정
)
