# TODO Implement TensegrityController and TestTensController
class TensegrityController(object):
    def __init__(self):
        pass

    def run_motors(self, freq_list):
        mNum = 1
        for fq in freq_list:
            print "Running motor {mNum} at {mFreq}".format(mNum=mNum,
                                                           mFreq=fq)
