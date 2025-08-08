import re
import os

class CodeParser:
    """Extracts code blocks from LLM responses"""
    
    def __init__(self):
        """Initialize the code extractor"""
        pass
        
    def extract_code_blocks(self, llm_response, language="python"):
        """
        Extract code blocks from an LLM response.
        
        Args:
            llm_response (str): The text response from the LLM API
            language (str): The programming language to extract (default: "python")
            
        Returns:
            list: List of extracted code blocks
        """
        # Pattern matches ```python ... ``` blocks
        # The regex uses non-greedy matching with .*? to handle multiple code blocks
        pattern = f"```{language}(.*?)```"
        
        # re.DOTALL allows the dot to match newlines
        matches = re.findall(pattern, llm_response, re.DOTALL)
        
        # Strip any leading/trailing whitespace from each match
        return [match.strip() for match in matches]


class CodeFileSaver:
    """Saves code to files in a specified directory"""
    
    def __init__(self, output_directory="generated_code"):
        """
        Initialize the code file saver with a default output directory.
        
        Args:
            output_directory (str): Directory to save the code files
        """
        self.output_directory = output_directory
        
        # Create the output directory if it doesn't exist
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)
    
    def save_code(self, code, filename):
        """
        Save code to a file in the configured output directory.
        
        Args:
            code (str): The code to save
            filename (str): Name of the file to save to
            
        Returns:
            str: Path to the saved file
        """
        # Make sure filename has the correct extension
        if not filename.endswith('.py'):
            filename = f"{filename}.py"
            
        # Join directory and filename
        file_path = os.path.join(self.output_directory, filename)
        
        # Write the code to the file
        with open(file_path, "w") as f:
            f.write(code)
            
        print(f"Code saved to {file_path}")
        return file_path
    
    def save_multiple_code_blocks(self, code_blocks, filename_base):
        """
        Save multiple code blocks to separate files.
        
        Args:
            code_blocks (list): List of code blocks to save
            filename_base (str): Base name for the output files
            
        Returns:
            list: Paths to the saved files
        """
        saved_files = []
        
        # Save each code block to a separate file
        for i, code in enumerate(code_blocks):
            if len(code_blocks) == 1:
                # If there's only one code block, use the base filename
                filename = f"{filename_base}.py"
            else:
                # If there are multiple code blocks, append an index
                filename = f"{filename_base}_{i+1}.py"
                
            file_path = self.save_code(code, filename)
            saved_files.append(file_path)
        
        return saved_files