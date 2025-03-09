# Dormitory Telegram Bot

This repository contains the source code for a Telegram bot designed to streamline dormitory management and improve communication between the dorm supervisor and students. The bot is divided into four main sections:

## 1. Request and Report
Students can submit reports regarding facility issues (e.g., maintenance problems, electrical or plumbing faults). After the dorm supervisor reviews these reports, they can send out the necessary notifications directly through the bot.

## 2. Feedback and Suggestions
This section collects general feedback, criticisms, and suggestions from students. The feedback is forwarded to the dorm supervisor for review and further action, helping improve overall dormitory management.

## 3. Accommodation Request
Students can submit accommodation or housing requests by providing details such as their student ID, national code, full name, etc. The bot performs basic data validation (e.g., checking character counts and correct formatting) before forwarding the request to the dorm supervisor for approval.

## 4. Lost and Found
In this section, students can report lost or found items by uploading photos and providing item descriptions along with their contact information. Submitted posts are sent to the dorm supervisor for approval. Once approved, the post is automatically published to a designated channel. Students also have the ability to view, edit, or delete their posts and request the removal of their contact information once the item is recovered.

## Message Organization
All messages and submissions are organized into separate topics within a group, allowing the dorm supervisor to review and manage all requests simultaneously. This organized structure ensures efficient handling of all dormitory-related communications.

## Overview
The primary goal of this Telegram bot is to facilitate and simplify dormitory management by centralizing various functions into one interactive platform. Whether it’s reporting maintenance issues, submitting accommodation requests, offering feedback, or managing lost and found items, the bot serves as a comprehensive tool for enhancing communication and operational efficiency between the dorm supervisor and students.

## Technologies
- Python
- Telegram Bot API
- Additional libraries for data validation and message handling
