import json
import re
import base64
from uuid import uuid4
from pathlib import Path
from loguru import logger
from typing import Optional, Union
import requests

from .utils.ut_error_handler import ErrorHandler
from seven2one.core_interface import ITechStack

class Email:

    def __init__(self, endpoint: str, techStack: ITechStack) -> None:
        self.techStack = techStack
        self.endpoint = endpoint

        self.header = {
            'AcceptEncoding': 'deflate',
            'Accept': 'application/json',
            'Content-type': 'application/json',
        }

        return

    def sendMail(
        self,
        to: Union[str, list],
        cc: Union[str, list,None] = None,
        bcc: Union[str, list,None] = None,
        subject: Optional[str] = None,
        textBody: Optional[str] = None,
        htmlBody: Optional[str] = None,
        attachments: Union[str, list,None] = None
    ) -> None:
        """
        Sends an email via the TechStack email service.

        Parameters:
        ----------
        to: str|list
            One or more recipient addresses.
        cc: str|list = None
            One or more recipient addresses in CC.
        bcc: str|list = None
            One or more recipient addresses in BCC.
        subject: str = None
            The email subject.
        textBody: str = None
            The text body of the email.
        htmlBody: str = None
            A HTML body of the email. Not, if both textBody and htmlBody are used,
            only the htmlBody will be sent.
        attachments: str|list = None
            Provide one or more file paths to attach files to the email.

        Examples:
        >>> sendMail('gustav@mail.com', cc=['annette@mail.com', carl@mail.com], subject='Hello', textBody=text)
        >>> sendMail('gustav@mail.com', attachments=['report.pdf', 'data.xlsx']
        """

        correlationId = str(uuid4())

        if isinstance(to, str):
            to = [to]
        if isinstance(cc, str):
            cc = [cc]
        if isinstance(bcc, str):
            bcc = [bcc]
        if isinstance(attachments, str):
            attachments = [attachments]

        address_regex = re.compile(
            r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
        for group in [to, cc, bcc]:
            if not group:
                continue
            for address in group:
                if not re.fullmatch(address_regex, address):
                    ErrorHandler.error(self.techStack.config.raiseException, f"Invalid email address '{address}'. Correlation ID: {correlationId}.")
                    return

        _attachments = []
        if attachments:
            for filepath in attachments:
                if not Path(filepath).exists():
                    ErrorHandler.error(self.techStack.config.raiseException, f"File path '{filepath}' is not correct. Correlation ID: {correlationId}.")
                    return
                with open(Path(filepath), 'rb') as file:
                    content = base64.b64encode(file.read()).decode('utf-8')
                    _attachments.append(
                        {'filename': Path(filepath).name, 'content': content})

        data = {
            'to': to,
            'subject': subject,
            'textBody': textBody,
            'htmlBody': htmlBody,
            'cc': cc,
            'bcc': bcc,
            'attachments': _attachments
        }

        data = json.dumps(data)

        with logger.contextualize(correlation_id=correlationId):
            headers = self.header.copy()
            headers['Authorization'] = f"Bearer {self.techStack.get_access_token()}"
            
            response = requests.post(url=self.endpoint, headers=headers, data=data)
            if response.status_code >= 400:
                logger.info(f'Email service not available. Response status {response.status_code}.')
            if response.status_code == 200:
                logger.info(f'Email sent to {to}.')

        return
