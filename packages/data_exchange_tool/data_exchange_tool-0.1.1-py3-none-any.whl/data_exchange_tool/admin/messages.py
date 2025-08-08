# TODO: add translations
ERROR_MODAL_MSG = """
    <button type="button" onclick="document.getElementById('{}').style.display='block'" style="padding:4px 8px;font-size:12px;border-radius: 10px;">
        Ver
    </button>
    <div id="{}" style="display:none;width:60%;max-height:500px;overflow:auto;padding:20px;background:white;border:1px solid #ccc;box-shadow:0 0 10px rgba(0,0,0,0.5);z-index:1000;position: absolute;top: 10%;left: 50%;transform: translate(-50%, -50%);margin-top:30px">
        <div style="text-align:right;">
            <button type='button' style='border-radius: 10px;' onclick="document.getElementById('{}').style.display='none'">Cerrar</button>
        </div>
        <pre style="white-space: pre-wrap;">{}</pre>
    </div>
"""

STATUS_HTML_TAG = """
    <span style="padding:2px 6px; color:white; background-color:{};
    border-radius:4px;display: block;text-align: center;">{}</span>
"""
SINGLE_JOB_ERROR_MSG = "Only single job can be changed."
ALLOWED_PREVIEW_STATUS_MSG = "Not able to preview job in {}. It should be one of {}"
ALLOWED_CONFIRM_STATUS_MSG = "Not able to confirm job in {}. It should be one of {}"
CONFIRM_WITH_ERRORS_MSG = "Not able to confirm job with errors."
