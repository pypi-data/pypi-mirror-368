#!/usr/bin/env python

# stdlib imports
import email.utils
import pathlib
import sys
from datetime import datetime
from email.mime.text import MIMEText
from smtplib import (
    SMTPDataError,
    SMTPHeloError,
    SMTPRecipientsRefused,
    SMTPSenderRefused,
)
from unittest.mock import Mock, patch

# local imports
from esi_utils_transfer import emailsender


def test_send():
    smtp_server = "fake.smtp.gov"
    sender = "fake.sender@email.gov"
    recipients = ["fake.receiver1@email.gov", "fake.receiver2@email.gov"]
    subject = "Yellow Alert, PAGER V1 279 km SE of Hotan, China"
    message = (
        "PAGER Version: 1\n"
        "279 km SE of Hotan, China\n"
        "GMT: 2020 / 06 / 25 - 21: 05\n"
        "MAG: 6.4\n"
        "LAT: 35.628\n"
        "LON: 82.452\n"
        "DEP: 10\n"
        "ID: us7000abmk"
    )
    props = {
        "smtp_servers": [smtp_server],
        "sender": sender,
        "subject": subject,
        "recipients": recipients,
        "message": message,
    }
    base_attrs = {
        "helo.return_value": (None, smtp_server),
        "sendmail.return_value": None,
    }

    # create a mocked SMTP *object*
    mock_smtp = Mock(**base_attrs)

    # patch the SMTP *class*
    with patch("esi_utils_transfer.emailsender.SMTP") as mocked_smtp:
        # tell the patched SMTP class to return our mocked SMTP object
        # instead of a real SMTP object
        mocked_smtp.return_value = mock_smtp
        # this should succeed
        sender = emailsender.EmailSender(properties=props)
        sender.send()

    thisfile = pathlib.Path(__file__)  # where is this script?
    thisdir = thisfile.parent  # what folder are we in?

    # test sending with file attachment
    # patch the SMTP *class*
    with patch("esi_utils_transfer.emailsender.SMTP") as mocked_smtp:
        # tell the patched SMTP class to return our mocked SMTP object
        # instead of a real SMTP object
        mocked_smtp.return_value = mock_smtp
        # this should succeed
        sender = emailsender.EmailSender(properties=props, local_files=[thisfile])
        sender.send()

    # test sending with zipped directory
    # patch the SMTP *class*
    with patch("esi_utils_transfer.emailsender.SMTP") as mocked_smtp:
        # tell the patched SMTP class to return our mocked SMTP object
        # instead of a real SMTP object
        mocked_smtp.return_value = mock_smtp
        # this should succeed
        zip_dict = {"zip_file": "allfiles.zip"}
        newprops = {**props, **zip_dict}
        sender = emailsender.EmailSender(
            properties=newprops, local_directory=str(thisdir)
        )
        sender.send()

    # test the cancel functionality
    with patch("esi_utils_transfer.emailsender.SMTP") as mocked_smtp:
        # tell the patched SMTP class to return our mocked SMTP object
        # instead of a real SMTP object
        mocked_smtp.return_value = mock_smtp
        # this should succeed
        zip_dict = {"zip_file": "allfiles.zip"}
        newprops = {**props, **zip_dict}
        sender = emailsender.EmailSender(properties=props)
        sender.cancel()

    # test the max_bcc functionality
    with patch("esi_utils_transfer.emailsender.SMTP") as mocked_smtp:
        # tell the patched SMTP class to return our mocked SMTP object
        # instead of a real SMTP object
        mocked_smtp.return_value = mock_smtp
        # this should succeed
        newprops = props.copy()
        for i in range(3, 30):
            recipient = f"fake.recipient{i}@email.gov"
            newprops["recipients"].append(recipient)
        newprops["max_bcc"] = 15
        sender = emailsender.EmailSender(properties=newprops)
        sender.send()

    # There are a number of ways that SMTP methods can fail. We're testing all of
    # the ones captured in emailsender.
    error_test_dict = {
        "Helo Error Test": (
            {"helo.side_effect": SMTPHeloError(0, "")},
            "Server did not respond to hello",
        ),
        "Recipients Refused Test": (
            {"send_message.side_effect": SMTPRecipientsRefused(0)},
            "Recipients refused",
        ),
        "Unexpected Error Code Test": (
            {"send_message.side_effect": SMTPDataError(1, "")},
            "Server responded with an unexpected error code",
        ),
        "Sender Refused Test": (
            {"send_message.side_effect": SMTPSenderRefused(0, "", "")},
            "Server refused sender address",
        ),
        "Catch-all Exception Test": (
            {"send_message.side_effect": BaseException()},
            "Connection to server failed (possible timeout)",
        ),
    }

    for test_title, test_tuple in error_test_dict.items():
        print(f"Running {test_title}...")
        test_attrs = test_tuple[0]
        test_comparison_string = test_tuple[1]
        attrs = {**base_attrs, **test_attrs}
        mock_smtp = Mock(**attrs)
        with patch("esi_utils_transfer.emailsender.SMTP") as mocked_smtp:
            mocked_smtp.return_value = mock_smtp
            sender = emailsender.EmailSender(properties=props)
            try:
                sender.send()
                raise AssertionError
            except Exception as e:
                assert test_comparison_string in str(e)


def real_send_test(server, address):
    for method in ["TLS", "STARTTLS", "SSL", "BOGUS"]:
        text = f"Testing secure email with method {method}."
        subject = f"Testing secure mail via {method}"
        props = {
            "smtp_servers": [server],
            "sender": address,
            "recipients": [address],
            "subject": "test",
            "message": text,
            "protocol": method,
            "max_bcc": 0,
        }
        this_file = pathlib.Path(__file__).resolve()
        sender = emailsender.EmailSender(properties=props, local_files=[this_file])
        print(f"Trying to send email using {method}...")
        try:
            response = sender.send()
            response = sender.cancel(cancel_content=f"Cancel using {method}")
            print(f"At {datetime.utcnow()}: response was '{response}'")
        except Exception as e:
            if method == "BOGUS":
                print(f"emailsender failed appropriately on method {method}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        server = sys.argv[1]
        address = sys.argv[2]
        real_send_test(server, address)
    test_send()
