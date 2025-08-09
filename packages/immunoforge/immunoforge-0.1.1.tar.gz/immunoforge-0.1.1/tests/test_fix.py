#!/usr/bin/env python3

from immunoforge.tools.netmhcpan import NetMHCpanTool

def test_fix():
    # Test with the exact peptides and alleles that were failing
    tool = NetMHCpanTool(
        executable="/tamir2/nicolaslynn/tools/netMHCpan-4.1/netMHCpan",
        mock_mode=False
    )
    
    peptides = ['YAAAVLFRMSEE', 'GILGFVFTL']
    alleles = ['HLA-A*02:01', 'HLA-B*07:02']
    
    try:
        result = tool.predict(peptides, alleles=alleles)
        print(f"Success! Shape: {result.shape}")
        print(f"Columns: {result.columns.tolist()}")
        print(result.head())
        return True
    except Exception as e:
        print(f"Still failing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_fix()