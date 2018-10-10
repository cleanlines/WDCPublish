'''
Workflow
for all three asset types
    just attach miisng data in \\DFSR01\Asset Data\ForwardWorks


log each process that completed ok
validation
republishing FWv
republsihing normal
'''

from ReportMissingAssets import ReportMissingAssets

def main():
    # step 1. Run validation
    ReportMissingAssets().execute_validation()
    # step 2. Join data
    print 2
    #publish FWP services
    #publish simple services



if __name__ == '__main__':
    main()