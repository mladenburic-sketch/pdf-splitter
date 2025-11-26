"""
Streamlit web application for splitting PDF files containing multiple invoices
"""

import streamlit as st
import tempfile
import os
from pathlib import Path
import zipfile
import shutil

from src.pdf_splitter import PDFSplitter


def create_zip_file(file_paths: list, output_path: Path) -> Path:
    """Create a ZIP file containing all the split PDF files"""
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in file_paths:
            zipf.write(file_path, Path(file_path).name)
    return output_path


def main():
    st.set_page_config(
        page_title="PDF Invoice Splitter",
        page_icon="📄",
        layout="wide"
    )
    
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


if __name__ == "__main__":
    main()

