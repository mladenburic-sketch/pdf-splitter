"""
Streamlit web application for splitting PDF files containing multiple invoices
and editing PDF files (text replacement)
"""

import streamlit as st
import tempfile
import os
from pathlib import Path
import zipfile
import shutil

from src.pdf_splitter import PDFSplitter
from src.pdf_editor import PDFEditor


def create_zip_file(file_paths: list, output_path: Path) -> Path:
    """Create a ZIP file containing all the split PDF files"""
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in file_paths:
            zipf.write(file_path, Path(file_path).name)
    return output_path


def pdf_splitter_page():
    """PDF Splitter page"""
    st.title("📄 PDF Invoice Splitter")
    st.markdown("Split a PDF file containing multiple invoices into individual PDF files")
    
    st.sidebar.header("Settings")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=['pdf'],
        help="Upload a PDF file containing multiple invoices"
    )
    
    # Invoice markers input
    st.sidebar.subheader("Invoice Detection")
    default_markers = ["Faktura", "Invoice", "Faktura br.", "Invoice No.", "Račun", "Bill"]
    custom_markers = st.sidebar.text_area(
        "Custom markers (one per line)",
        value="\n".join(default_markers),
        help="Enter markers that indicate the start of a new invoice. One marker per line."
    )
    
    # Regex pattern option
    use_regex = st.sidebar.checkbox("Use regex pattern instead", value=False)
    regex_pattern = None
    if use_regex:
        regex_pattern = st.sidebar.text_input(
            "Regex pattern",
            value=r"Faktura\s+br\.\s*\d+",
            help="Regular expression pattern to identify invoice starts"
        )
    
    # Process button
    if uploaded_file is not None:
        st.success(f"File uploaded: **{uploaded_file.name}**")
        st.info(f"File size: {uploaded_file.size / 1024:.2f} KB")
        
        if st.button("🚀 Split PDF", type="primary", use_container_width=True):
            with st.spinner("Processing PDF file..."):
                try:
                    # Create temporary directory for processing
                    with tempfile.TemporaryDirectory() as temp_dir:
                        temp_input = Path(temp_dir) / uploaded_file.name
                        temp_output = Path(temp_dir) / "output"
                        
                        # Save uploaded file to temp directory
                        with open(temp_input, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        
                        # Parse markers
                        markers = None
                        if not use_regex:
                            markers = [m.strip() for m in custom_markers.split("\n") if m.strip()]
                        
                        # Initialize splitter and split invoices
                        splitter = PDFSplitter(str(temp_input), str(temp_output))
                        output_files = splitter.split_invoices(
                            invoice_markers=markers,
                            page_start_pattern=regex_pattern
                        )
                        
                        if output_files:
                            st.success(f"✅ Successfully created {len(output_files)} invoice files!")
                            
                            # Display results
                            st.subheader("📋 Generated Files")
                            
                            # Create ZIP file for download
                            zip_path = temp_output / "invoices.zip"
                            create_zip_file(output_files, zip_path)
                            
                            # Display download buttons
                            col1, col2 = st.columns(2)
                            
                            # Read ZIP file once for reuse
                            with open(zip_path, "rb") as zip_file:
                                zip_data = zip_file.read()
                            
                            with col1:
                                st.download_button(
                                    label="📦 Download All (ZIP)",
                                    data=zip_data,
                                    file_name=f"{Path(uploaded_file.name).stem}_invoices.zip",
                                    mime="application/zip",
                                    use_container_width=True,
                                    key="zip_download_col1"
                                )
                            
                            with col2:
                                # Show individual files
                                st.markdown("**Individual files:**")
                                for i, file_path in enumerate(output_files, 1):
                                    file_name = Path(file_path).name
                                    with open(file_path, "rb") as f:
                                        st.download_button(
                                            label=f"📄 {file_name}",
                                            data=f.read(),
                                            file_name=file_name,
                                            key=f"file_{i}",
                                            use_container_width=True
                                        )
                            
                            # Main download button below generated files
                            st.markdown("---")
                            st.download_button(
                                label="⬇️ Download All Invoices (ZIP Archive)",
                                data=zip_data,
                                file_name=f"{Path(uploaded_file.name).stem}_invoices.zip",
                                mime="application/zip",
                                type="primary",
                                use_container_width=True,
                                key="main_download"
                            )
                            
                            # Show summary table
                            st.subheader("📊 Summary")
                            summary_data = []
                            for i, file_path in enumerate(output_files, 1):
                                file_size = os.path.getsize(file_path) / 1024  # KB
                                summary_data.append({
                                    "Invoice #": i,
                                    "File Name": Path(file_path).name,
                                    "Size (KB)": f"{file_size:.2f}"
                                })
                            
                            st.dataframe(summary_data, use_container_width=True, hide_index=True)
                        else:
                            st.error("No invoices found in the PDF file. Please check your markers or pattern.")
                
                except FileNotFoundError as e:
                    st.error(f"❌ Error: {str(e)}")
                except ValueError as e:
                    st.error(f"❌ Error: {str(e)}")
                except Exception as e:
                    st.error(f"❌ Unexpected error: {str(e)}")
                    st.exception(e)
    
    else:
        st.info("👆 Please upload a PDF file to get started")
        
        # Instructions
        with st.expander("ℹ️ How to use"):
            st.markdown("""
            ### Instructions:
            1. **Upload a PDF file** containing multiple invoices
            2. **Configure markers** (optional) - specify text that indicates the start of a new invoice
            3. **Click "Split PDF"** to process the file
            4. **Download** the individual invoice files or the complete ZIP archive
            
            ### Default Markers:
            The application will look for common invoice indicators like:
            - "Faktura", "Invoice"
            - "Faktura br.", "Invoice No."
            - "Račun", "Bill"
            
            You can customize these markers in the sidebar.
            
            ### Tips:
            - Make sure your PDF contains searchable text (not just images)
            - If invoices don't split correctly, try adjusting the markers
            - Use regex pattern for more advanced matching
            """)


def pdf_editor_page():
    """PDF Editor page"""
    st.title("✏️ PDF Editor")
    st.markdown("Upload a PDF file, replace text, and download the edited PDF")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose a PDF file to edit",
        type=['pdf'],
        help="Upload a PDF file that you want to edit"
    )
    
    if uploaded_file is not None:
        st.success(f"File uploaded: **{uploaded_file.name}**")
        st.info(f"File size: {uploaded_file.size / 1024:.2f} KB")
        
        st.markdown("---")
        st.subheader("Text Replacement")
        
        # Initialize session state for replacements
        if 'replacements' not in st.session_state:
            st.session_state.replacements = [{"old": "", "new": ""}]
        
        # Display replacement fields
        for i, replacement in enumerate(st.session_state.replacements):
            col1, col2, col3 = st.columns([3, 3, 1])
            
            with col1:
                old_text = st.text_input(
                    f"Text to replace (old value) #{i+1}",
                    value=replacement["old"],
                    key=f"old_{i}",
                    help="Enter the text you want to replace in the PDF"
                )
                st.session_state.replacements[i]["old"] = old_text
            
            with col2:
                new_text = st.text_input(
                    f"New text (replacement value) #{i+1}",
                    value=replacement["new"],
                    key=f"new_{i}",
                    help="Enter the new text that will replace the old text"
                )
                st.session_state.replacements[i]["new"] = new_text
            
            with col3:
                st.write("")  # Spacing
                st.write("")  # Spacing
                if st.button("🗑️", key=f"remove_{i}", help="Remove this replacement"):
                    st.session_state.replacements.pop(i)
                    st.rerun()
        
        # Add new replacement button
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("➕ Add Replacement", use_container_width=True):
                st.session_state.replacements.append({"old": "", "new": ""})
                st.rerun()
        
        st.markdown("---")
        
        # Process button
        if st.button("🔄 Replace All Text", type="primary", use_container_width=True):
            # Validate replacements
            valid_replacements = {}
            has_errors = False
            
            for i, replacement in enumerate(st.session_state.replacements):
                old_text = replacement["old"].strip()
                new_text = replacement["new"]
                
                if old_text:
                    valid_replacements[old_text] = new_text
                elif old_text == "" and new_text != "":
                    st.warning(f"⚠️ Replacement #{i+1}: Old text is empty, skipping...")
            
            if not valid_replacements:
                st.error("❌ Please enter at least one text replacement (old value is required)")
            else:
                with st.spinner("Processing PDF file..."):
                    try:
                        # Create temporary directory for processing
                        with tempfile.TemporaryDirectory() as temp_dir:
                            temp_input = Path(temp_dir) / uploaded_file.name
                            temp_output = Path(temp_dir) / f"{Path(uploaded_file.name).stem}_edited.pdf"
                            
                            # Save uploaded file to temp directory
                            with open(temp_input, "wb") as f:
                                f.write(uploaded_file.getbuffer())
                            
                            # Initialize editor and replace text
                            editor = PDFEditor(str(temp_input))
                            
                            # Use replace_text_multiple if more than one replacement, otherwise use replace_text
                            if len(valid_replacements) == 1:
                                old_text, new_text = next(iter(valid_replacements.items()))
                                output_path = editor.replace_text(old_text, new_text, str(temp_output))
                            else:
                                output_path = editor.replace_text_multiple(valid_replacements, str(temp_output))
                            
                            if output_path and Path(output_path).exists():
                                st.success(f"✅ PDF successfully edited! ({len(valid_replacements)} replacement(s) applied)")
                                
                                # Display download button
                                with open(output_path, "rb") as f:
                                    pdf_data = f.read()
                                
                                st.download_button(
                                    label="⬇️ Download Edited PDF",
                                    data=pdf_data,
                                    file_name=f"{Path(uploaded_file.name).stem}_edited.pdf",
                                    mime="application/pdf",
                                    type="primary",
                                    use_container_width=True
                                )
                                
                                # Show file info
                                file_size = os.path.getsize(output_path) / 1024  # KB
                                st.info(f"📊 Edited file size: {file_size:.2f} KB")
                                
                                # Show summary of replacements
                                with st.expander("📋 Replacement Summary"):
                                    summary_data = []
                                    for old, new in valid_replacements.items():
                                        summary_data.append({
                                            "Old Text": old[:50] + ("..." if len(old) > 50 else ""),
                                            "New Text": new[:50] + ("..." if len(new) > 50 else "")
                                        })
                                    st.dataframe(summary_data, use_container_width=True, hide_index=True)
                            else:
                                st.error("❌ Failed to create edited PDF")
                    
                    except ImportError as e:
                        st.error(f"❌ Error: {str(e)}")
                        st.info("💡 Please install PyMuPDF: pip install PyMuPDF")
                    except FileNotFoundError as e:
                        st.error(f"❌ Error: {str(e)}")
                    except ValueError as e:
                        st.error(f"❌ Error: {str(e)}")
                    except Exception as e:
                        st.error(f"❌ Unexpected error: {str(e)}")
                        st.exception(e)
    
    else:
        st.info("👆 Please upload a PDF file to get started")
        
        # Instructions
        with st.expander("ℹ️ How to use"):
            st.markdown("""
            ### Instructions:
            1. **Upload a PDF file** that you want to edit
            2. **Enter the old text** that you want to replace
            3. **Enter the new text** that will replace the old text
            4. **Click "➕ Add Replacement"** to add more text replacements (optional)
            5. **Click "🔄 Replace All Text"** to process the file with all replacements
            6. **Download** the edited PDF file
            
            ### Notes:
            - The text replacement is case-sensitive
            - All occurrences of the old text will be replaced
            - The PDF must contain searchable text (not just images)
            - Formatting may be slightly affected after text replacement
            
            ### Tips:
            - Make sure your PDF contains searchable text (not scanned images)
            - Use exact text matching (case-sensitive)
            - You can add multiple replacements and apply them all at once
            - Click the 🗑️ button to remove a replacement field
            """)


def main():
    st.set_page_config(
        page_title="PDF Tools",
        page_icon="📄",
        layout="wide"
    )
    
    # Create tabs
    tab1, tab2 = st.tabs(["📄 PDF Splitter", "✏️ PDF Editor"])
    
    with tab1:
        pdf_splitter_page()
    
    with tab2:
        pdf_editor_page()


if __name__ == "__main__":
    main()

