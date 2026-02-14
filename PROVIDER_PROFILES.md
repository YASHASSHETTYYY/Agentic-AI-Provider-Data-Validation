
# Revised UI for Verified & Updated Provider Profiles

This document outlines a revised UI layout for the "Verified & Updated Provider Profiles" section, designed to be more user-friendly, compact, and efficient for healthcare payer operations teams. The design prioritizes instant visibility of key information with options for progressive disclosure.

This design is well-suited for implementation in Streamlit, given the project's dependencies.

## 1. UI Layout Description & Component Structure

The proposed layout uses a hybrid table-and-card approach, where each provider is represented by a compact row that is easy to scan. The rows will contain key information visible by default, and an expander for more details.

Here’s a breakdown of the components for each provider row:

---

### **Default View (Always Visible)**

This part of the row will be structured using columns to align information for easy scanning.

| Component                 | Description                                                                                                                                                             | Streamlit Implementation suggestion |
| ------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------- |
| **Provider Name**         | The full name of the provider.                                                                                                                                          | `st.markdown("#### Dr. Jane Smith")`  |
| **Specialty**             | The provider's specialty.                                                                                                                                               | `st.markdown("_Cardiology_")`         |
| **Validation Status**     | A colored badge indicating the status.                                                                                                                                  | `st.markdown(f'<span style="background-color: {color}; color: white; padding: 5px; border-radius: 5px;">{status}</span>', unsafe_allow_html=True)` |
| **Confidence Score**      | A progress bar to visually represent the confidence score.                                                                                                              | `st.progress(score)`                |
| **Key Issues Detected**   | A short list of critical issues found during validation (if any).                                                                                                         | `st.multiselect` or `st.markdown` with bullet points. |
| **Quick Actions**         | Inline buttons for common actions. These will be smaller and less prominent than the main data.                                                                         | `st.button("View Evidence")`, `st.button("Flag for Review")` inside `st.columns` |

### **Expanded View (Progressive Disclosure)**

Clicking on a provider row will expand it to show more detailed information. This can be achieved using an expander component.

- **Source-Level Details:** A table showing the data from different sources (e.g., NPI, PECOS, CAQH).
- **Before vs. After:** A side-by-side comparison of data changes.
- **Validation Reasoning:** A log or explanation of the validation steps and logic.

This would be contained within an `st.expander`.

## 2. Example Data Structure

The following Python dictionary structure (which can be easily converted to a Pandas DataFrame) would support this UI.

```python
[
    {
        "provider_name": "Dr. John Doe",
        "specialty": "Pediatrics",
        "validation_status": "Verified",
        "confidence_score": 0.95,
        "key_issues": [],
        "details": {
            "source_validation": {
                "NPI": {"status": "Verified", "data": {...}},
                "PECOS": {"status": "Verified", "data": {...}},
            },
            "data_changes": {"before": {...}, "after": {...}},
            "validation_log": ["Step 1:...", "Step 2:..."]
        }
    },
    {
        "provider_name": "Dr. Jane Smith",
        "specialty": "Cardiology",
        "validation_status": "Updated",
        "confidence_score": 0.80,
        "key_issues": ["Address Mismatch", "NPI not found"],
        "details": {
            "source_validation": {
                "NPI": {"status": "Failed", "data": {...}},
                "PECOS": {"status": "Verified", "data": {...}},
            },
            "data_changes": {"before": {"address": "..."}, "after": {"address": "..."}},
            "validation_log": ["Step 1:...", "Step 2:..."]
        }
    },
    {
        "provider_name": "Dr. Emily White",
        "specialty": "Oncology",
        "validation_status": "Needs Review",
        "confidence_score": 0.45,
        "key_issues": ["License Expired", "Multiple conflicting records"],
        "details": {
            "source_validation": {
                "NPI": {"status": "Verified", "data": {...}},
                "State License": {"status": "Failed", "reason": "Expired"},
            },
            "data_changes": {"before": {...}, "after": {...}},
            "validation_log": ["Step 1:...", "Step 2:..."]
        }
    }
]
```

## 3. How the New UI Improves User Experience

This revised design directly addresses the problems with the current UI:

- **Usability:** By making key information visible by default, users can immediately assess the situation without any clicks. The layout is clean and follows a logical hierarchy.
- **Speed of Decision-Making:** Payer operations teams can now scan the list of providers quickly. The color-coded statuses and confidence scores allow for rapid identification of providers that need attention. This transforms the workflow from "click and wait" to "scan and act".
- **User Experience:** The new design feels more modern, responsive, and professional. It respects the user's time by providing information efficiently. The progressive disclosure mechanism ensures that the UI is not cluttered, while still providing deep-dive capabilities when needed.

This UI transforms the results screen from "Click to see results" to "Results are visible instantly, with optional deep-dive," meeting all the success criteria you outlined.
I will now create the file `app/main.py`, which will contain a basic implementation of the concepts that I have shown above.
I will use the `write_file` to create this file.

## 4. Visualizations Used

- **Bar Chart: Providers by confidence score range**
- **Pie Chart: Risk-level distribution**
- **Heat Map: High-risk providers by location/specialty**
- **Before–After Table: Field-level data corrections**
