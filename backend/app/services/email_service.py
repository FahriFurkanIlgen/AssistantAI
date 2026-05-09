"""
Email Service - SMTP-based transactional email sending.
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings


def send_cancel_otp_email(
    to_email: str,
    customer_name: str,
    appointment_summary: str,
    otp_code: str,
    business_name: str,
) -> None:
    """Send OTP cancellation code to customer email via SMTP."""
    subject = f"Randevu İptal Kodu – {business_name}"

    html_body = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 480px; margin: 0 auto; padding: 32px 24px; background: #ffffff;">
      <h2 style="font-size: 22px; color: #1d1d1f; margin-bottom: 8px;">{business_name}</h2>
      <p style="color: #6e6e73; font-size: 14px; margin-bottom: 24px;">Randevu İptal Doğrulama</p>

      <p style="color: #1d1d1f; font-size: 15px;">Merhaba <strong>{customer_name}</strong>,</p>
      <p style="color: #1d1d1f; font-size: 15px;">Aşağıdaki randevunuzu iptal etmek için bir istek aldık:</p>
      <div style="background: #f5f5f7; border-radius: 12px; padding: 16px; margin: 20px 0;">
        <p style="margin: 0; color: #1d1d1f; font-size: 14px;">{appointment_summary}</p>
      </div>

      <p style="color: #1d1d1f; font-size: 15px;">İptal işlemini onaylamak için aşağıdaki kodu chatbot'a girin:</p>
      <div style="text-align: center; margin: 28px 0;">
        <span style="font-size: 36px; font-weight: 700; letter-spacing: 8px; color: #0071e3; font-family: monospace;">{otp_code}</span>
      </div>

      <p style="color: #6e6e73; font-size: 13px;">Bu kod 10 dakika geçerlidir. İptal talebinde bulunmadıysanız bu e-postayı dikkate almayın.</p>
      <hr style="border: none; border-top: 1px solid #d2d2d7; margin: 24px 0;">
      <p style="color: #6e6e73; font-size: 12px; margin: 0;">{business_name} — Otomatik gönderim, lütfen yanıtlamayın.</p>
    </div>
    """

    text_body = (
        f"{business_name} - Randevu İptal Kodu\n\n"
        f"Merhaba {customer_name},\n"
        f"Randevu: {appointment_summary}\n\n"
        f"İptal kodu: {otp_code}\n\n"
        f"Bu kod 10 dakika geçerlidir."
    )

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{business_name} <{settings.SMTP_FROM}>"
    msg["To"] = to_email
    msg.attach(MIMEText(text_body, "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.ehlo()
        if settings.SMTP_TLS:
            server.starttls()
        if settings.SMTP_USER and settings.SMTP_PASSWORD:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.sendmail(settings.SMTP_FROM, to_email, msg.as_string())


def send_confirmation_email(
    to_email: str,
    customer_name: str,
    service_name: str,
    start_time: str,
    end_time: str,
    business_name: str,
    business_phone: str = "",
) -> None:
    """Send appointment confirmation email to the customer."""
    subject = f"Randevu Onayı – {business_name}"

    html_body = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 480px; margin: 0 auto; padding: 32px 24px; background: #ffffff;">
      <h2 style="font-size: 22px; color: #1d1d1f; margin-bottom: 4px;">{business_name}</h2>
      <p style="color: #6e6e73; font-size: 14px; margin-bottom: 24px;">Randevu Onayı</p>

      <p style="color: #1d1d1f; font-size: 15px;">Merhaba <strong>{customer_name}</strong>,</p>
      <p style="color: #1d1d1f; font-size: 15px; margin-bottom: 20px;">
        Randevunuz başarıyla oluşturuldu. Ayrıntılar aşağıdadır:
      </p>

      <div style="background: #f5f5f7; border-radius: 12px; padding: 20px; margin-bottom: 24px;">
        <table style="width:100%; border-collapse: collapse;">
          <tr>
            <td style="color: #6e6e73; font-size: 13px; padding-bottom: 10px; width: 40%;">Hizmet</td>
            <td style="color: #1d1d1f; font-size: 14px; font-weight: 600; padding-bottom: 10px;">{service_name}</td>
          </tr>
          <tr>
            <td style="color: #6e6e73; font-size: 13px; padding-bottom: 10px;">Tarih &amp; Saat</td>
            <td style="color: #1d1d1f; font-size: 14px; font-weight: 600; padding-bottom: 10px;">{start_time}</td>
          </tr>
          <tr>
            <td style="color: #6e6e73; font-size: 13px;">Bitiş</td>
            <td style="color: #1d1d1f; font-size: 14px; font-weight: 600;">{end_time}</td>
          </tr>
        </table>
      </div>

      {"<p style='color: #1d1d1f; font-size: 14px;'>Sorularınız için: <strong>" + business_phone + "</strong></p>" if business_phone else ""}

      <p style="color: #6e6e73; font-size: 13px; margin-top: 24px;">
        Randevunuzu iptal etmek istiyorsanız chatbot üzerinden talepte bulunabilirsiniz.
      </p>
      <hr style="border: none; border-top: 1px solid #d2d2d7; margin: 24px 0;">
      <p style="color: #6e6e73; font-size: 12px; margin: 0;">{business_name} — Otomatik gönderim, lütfen yanıtlamayın.</p>
    </div>
    """

    text_body = (
        f"{business_name} - Randevu Onayı\n\n"
        f"Merhaba {customer_name},\n"
        f"Randevunuz oluşturuldu.\n\n"
        f"Hizmet: {service_name}\n"
        f"Tarih & Saat: {start_time}\n"
        f"Bitiş: {end_time}\n\n"
        f"{('İletişim: ' + business_phone + chr(10)) if business_phone else ''}"
        f"İptal için chatbot üzerinden talep oluşturabilirsiniz."
    )

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{business_name} <{settings.SMTP_FROM}>"
    msg["To"] = to_email
    msg.attach(MIMEText(text_body, "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.ehlo()
        if settings.SMTP_TLS:
            server.starttls()
        if settings.SMTP_USER and settings.SMTP_PASSWORD:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.sendmail(settings.SMTP_FROM, to_email, msg.as_string())
