# libero-lab

[LIBERO](https://github.com/Lifelong-Robot-Learning/LIBERO) 벤치마크를 VLA 연구에 쓰기 위한 작업 공간.

업스트림은 **2025-03(`8f1084e`) 이후 멈춰 있어** 최신 환경에서 그대로 동작하지 않는다.
이 저장소는 설치를 재현 가능하게 만들고, 벤치마크 내부를 직접 확인한 기록을 함께 둔다.

```bash
git clone --recursive <이 저장소>
./setup.sh
.venv/bin/python run_demo.py --suite libero_spatial --task 0 --gui
```

macOS(Apple Silicon)와 CUDA 리눅스 양쪽에서 검증했다.

## 무엇이 들어 있나

| | |
|---|---|
| `setup.sh` | 환경 구축 — 업스트림 버그 8건 우회를 포함한다 |
| `patches/` | LIBERO 소스 수정분. 서브모듈은 수정을 담지 못하므로 패치로 관리 |
| `run_demo.py` | 태스크 목록·GUI 실행·영상 저장 |
| `replay_demo.py` | 사람 시연 데모 재생 (데이터셋 필요) |
| `CLAUDE.md` | **작업 문서** — 버그 목록, 검증된 사실, 다음 할 일 |

## 왜 설치가 까다로운가

`libero`의 `setup.py`가 `install_requires=[]`라 **의존성을 하나도 선언하지 않는다.**
`pip install -e`가 아무것도 끌어오지 않고 버전 충돌도 막지 못한다.
`robosuite 1.4.1`은 `mujoco 2.3.x` API 기준인데 최신 mujoco를 설치하면 조용히 깨진다.

그 외에 마주치는 것들 — 네임스페이스 패키지 미인식, `torch.load` 기본값 변경,
macOS의 OpenGL 경로, Linux 전용 `egl_probe`, `--datasets all`의 이름 불일치.
전부 `setup.sh`와 `patches/`가 처리하며, 목록과 원인은 [CLAUDE.md](CLAUDE.md)에 있다.

## 데이터셋

**평가만 한다면 받을 필요가 없다.** 평가 시작점(`.pruned_init`)은 LIBERO 저장소에
포함되어 있고, 전부 합쳐 13 MB다. 100 GB 데모는 직접 모방학습을 할 때만 쓴다.

## 라이선스

이 저장소의 스크립트와 문서는 **MIT** ([LICENSE](LICENSE)).

의존하는 것들도 모두 허용적 라이선스다 — LIBERO · robosuite · bddl · robomimic 은 MIT,
MuJoCo 는 Apache 2.0.

`patches/libero-fixes.patch` 는 LIBERO 소스의 파생물이므로 원 저작권 고지를
[patches/NOTICE.md](patches/NOTICE.md) 에 함께 둔다.
`ref/` 의 이미지는 [ref/SOURCES.md](ref/SOURCES.md) 의 출처·라이선스 표기를 따른다.
