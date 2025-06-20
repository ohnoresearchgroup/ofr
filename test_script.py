from OHExp import OFR_Data

input_file = r"C:\Users\mikeb\OneDrive\Documents\GitHub\ofr\PAMData20250612_1.xlsx"

ofr = OFR_Data(input_file)
ofr.calc_UV()
ofr.calc_h2o_mr()
ofr.calc_OHR_ext()   # NO argument here
ofr.calc_oh_exp()

print(ofr.df[['dat', 'OHexp_molec_cm3_s']].head())

output_file = r"C:\Users\mikeb\OneDrive\Documents\GitHub\ofr\PAMData20250612_1_processed.xlsx"
ofr.df.to_excel(output_file, index=False)


