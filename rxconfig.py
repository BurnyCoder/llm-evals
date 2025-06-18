import reflex as rx

config = rx.Config(
    app_name="llm_evals",
    plugins=[rx.plugins.TailwindV3Plugin()],
    frontend_packages=[
        "marked"
    ],
)